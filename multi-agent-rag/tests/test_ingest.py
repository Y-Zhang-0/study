"""Tests for Ingest Pipeline."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
from src.rag.ingest import IngestPipeline


@pytest.fixture
def mock_parser():
    """Mock document parser."""
    parser = Mock()
    parser.parse = Mock(return_value="Parsed content")
    return parser


@pytest.fixture
def mock_chunker():
    """Mock text chunker."""
    chunker = Mock()
    chunker.chunk = Mock(return_value=[
        {"content": "Chunk 1", "metadata": {"index": 0}},
        {"content": "Chunk 2", "metadata": {"index": 1}}
    ])
    return chunker


@pytest.fixture
def mock_embedding():
    """Mock embedding provider."""
    embedding = Mock()
    embedding.embed_batch = AsyncMock(return_value=[[0.1, 0.2], [0.3, 0.4]])
    return embedding


@pytest.fixture
def mock_vector_store():
    """Mock vector store."""
    store = Mock()
    store.add_documents = AsyncMock()
    return store


@pytest.fixture
def ingest_pipeline(mock_parser, mock_chunker, mock_embedding, mock_vector_store):
    """Create ingest pipeline with mocks."""
    return IngestPipeline(
        parser=mock_parser,
        chunker=mock_chunker,
        embedding=mock_embedding,
        vector_store=mock_vector_store
    )


@pytest.mark.asyncio
async def test_ingest_single_document(ingest_pipeline, mock_parser, mock_chunker, mock_embedding, mock_vector_store):
    """Test ingesting a single document."""
    test_file = Path("test.md")

    await ingest_pipeline.ingest_document(test_file)

    mock_parser.parse.assert_called_once_with(test_file)
    mock_chunker.chunk.assert_called_once()
    mock_embedding.embed_batch.assert_called_once()
    mock_vector_store.add_documents.assert_called_once()


@pytest.mark.asyncio
async def test_ingest_directory(ingest_pipeline, mock_parser, mock_chunker):
    """Test ingesting directory of documents."""
    with patch('pathlib.Path.glob') as mock_glob:
        mock_glob.side_effect = [
            [Path("doc1.md"), Path("doc2.md")],
            []
        ]

        result = await ingest_pipeline.ingest_directory(Path("docs"))

        assert result["processed"] == 2
