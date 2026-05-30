# tests/test_embedding.py
import pytest
from src.infrastructure.embedding import LocalEmbedding


def test_local_embedding_encode():
    """测试本地 embedding 编码"""
    embedding = LocalEmbedding()
    texts = ["hello world", "test document"]

    vectors = embedding.encode(texts)

    assert len(vectors) == 2
    assert len(vectors[0]) > 0  # 向量维度 > 0
    assert isinstance(vectors[0][0], float)
