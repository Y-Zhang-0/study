# src/infrastructure/vector_store.py
import chromadb
from chromadb.config import Settings


class VectorStore:
    """ChromaDB 向量存储封装"""

    def __init__(
        self,
        collection_name: str = "documents",
        persist_directory: str | None = None
    ):
        """
        初始化向量存储

        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录，None表示使用内存模式
        """
        self.collection_name = collection_name

        if persist_directory:
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.Client(Settings(
                is_persistent=False,
                allow_reset=True
            ))

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        ids: list[str],
        metadatas: list[dict] | None = None
    ) -> None:
        """
        添加文档到向量存储

        Args:
            texts: 文档文本列表
            embeddings: 向量列表
            ids: 文档ID列表
            metadatas: 元数据列表
        """
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict | None = None
    ) -> dict:
        """
        查询相似文档

        Args:
            query_embedding: 查询向量
            n_results: 返回结果数量
            where: 元数据过滤条件

        Returns:
            包含ids, documents, distances, metadatas的字典
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )

        return {
            "ids": results["ids"][0] if results["ids"] else [],
            "documents": results["documents"][0] if results["documents"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else []
        }

    def delete(self, ids: list[str]) -> None:
        """
        删除文档

        Args:
            ids: 要删除的文档ID列表
        """
        self.collection.delete(ids=ids)

    def clear(self) -> None:
        """清空集合中的所有文档"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def count(self) -> int:
        """返回集合中的文档数量"""
        return self.collection.count()
