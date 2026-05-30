# tests/test_vector_store.py
import pytest
from src.infrastructure.vector_store import VectorStore


@pytest.fixture
def vector_store():
    """创建临时向量存储实例"""
    store = VectorStore(collection_name="test_collection", persist_directory=None)
    yield store
    # 清理
    try:
        store.client.delete_collection("test_collection")
    except Exception:
        pass


def test_vector_store_initialization(vector_store):
    """测试向量存储初始化"""
    assert vector_store.collection_name == "test_collection"
    assert vector_store.collection is not None


def test_add_documents(vector_store):
    """测试添加文档"""
    texts = ["Hello world", "Test document"]
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    ids = ["doc1", "doc2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]

    vector_store.add(
        texts=texts,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )

    # 验证文档已添加
    count = vector_store.collection.count()
    assert count == 2


def test_query_documents(vector_store):
    """测试查询文档"""
    # 先添加文档
    texts = ["Python programming", "Machine learning", "Data science"]
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
    ids = ["doc1", "doc2", "doc3"]

    vector_store.add(texts=texts, embeddings=embeddings, ids=ids)

    # 查询
    query_embedding = [0.15, 0.25, 0.35]
    results = vector_store.query(query_embedding=query_embedding, n_results=2)

    assert len(results["ids"]) == 2
    assert len(results["documents"]) == 2
    assert len(results["distances"]) == 2


def test_delete_documents(vector_store):
    """测试删除文档"""
    texts = ["Doc 1", "Doc 2", "Doc 3"]
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
    ids = ["doc1", "doc2", "doc3"]

    vector_store.add(texts=texts, embeddings=embeddings, ids=ids)
    assert vector_store.collection.count() == 3

    # 删除一个文档
    vector_store.delete(ids=["doc2"])
    assert vector_store.collection.count() == 2


def test_clear_collection(vector_store):
    """测试清空集合"""
    texts = ["Doc 1", "Doc 2"]
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    ids = ["doc1", "doc2"]

    vector_store.add(texts=texts, embeddings=embeddings, ids=ids)
    assert vector_store.collection.count() == 2

    vector_store.clear()
    assert vector_store.collection.count() == 0
