"""Tests for document chunker."""
import pytest
from src.rag.chunker import Chunker, ChunkMetadata


class TestChunker:
    """Test chunker functionality."""

    def test_chunk_by_tokens_basic(self):
        """Test basic token-based chunking."""
        chunker = Chunker(chunk_size=10, overlap=2)
        text = "This is a test document with multiple sentences. " * 5

        chunks = chunker.chunk_by_tokens(text)

        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk, str)
            assert len(chunk) > 0

    def test_chunk_by_tokens_with_metadata(self):
        """Test chunking with metadata."""
        chunker = Chunker(chunk_size=10, overlap=2)
        text = "Test content for chunking."
        metadata = {"source": "test.txt", "page": 1}

        chunks = chunker.chunk_by_tokens(text, metadata=metadata)

        assert len(chunks) > 0

    def test_chunk_by_sentences(self):
        """Test sentence-based chunking."""
        chunker = Chunker(chunk_size=50, overlap=10)
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."

        chunks = chunker.chunk_by_sentences(text)

        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk, str)

    def test_empty_text(self):
        """Test chunking empty text."""
        chunker = Chunker(chunk_size=10, overlap=2)

        chunks = chunker.chunk_by_tokens("")

        assert len(chunks) == 0

    def test_overlap_validation(self):
        """Test overlap must be less than chunk_size."""
        with pytest.raises(ValueError):
            Chunker(chunk_size=10, overlap=15)


class TestChunkMetadata:
    """Test chunk metadata."""

    def test_metadata_creation(self):
        """Test creating chunk metadata."""
        metadata = ChunkMetadata(
            chunk_id="chunk_1",
            source="test.txt",
            start_pos=0,
            end_pos=100,
            chunk_index=0
        )

        assert metadata.chunk_id == "chunk_1"
        assert metadata.source == "test.txt"
        assert metadata.start_pos == 0
        assert metadata.end_pos == 100
        assert metadata.chunk_index == 0

    def test_metadata_to_dict(self):
        """Test converting metadata to dict."""
        metadata = ChunkMetadata(
            chunk_id="chunk_1",
            source="test.txt",
            start_pos=0,
            end_pos=100,
            chunk_index=0
        )

        result = metadata.to_dict()

        assert isinstance(result, dict)
        assert result["chunk_id"] == "chunk_1"
        assert result["source"] == "test.txt"
