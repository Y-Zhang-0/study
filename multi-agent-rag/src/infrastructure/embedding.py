# src/infrastructure/embedding.py
from sentence_transformers import SentenceTransformer
from src.config import settings


class LocalEmbedding:
    """本地 Embedding (sentence-transformers)"""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings().embedding_model
        self.device = settings().embedding_device
        self.model = SentenceTransformer(self.model_name, device=self.device)

    def encode(self, texts: list[str]) -> list[list[float]]:
        """编码文本为向量"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """向量维度"""
        return self.model.get_sentence_embedding_dimension()
