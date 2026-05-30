"""Integration tests for Multi-Agent RAG system."""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from src.rag.ingest import IngestPipeline
from src.agents.orchestrator import OrchestratorAgent
from src.agents.retriever import RetrieverAgent
from src.agents.analyzer import AnalyzerAgent
from src.infrastructure.message import Message


@pytest.fixture
def mock_components():
    """Mock all infrastructure components."""
    parser = MagicMock()
    parser.parse.return_value = "Test content"

    chunker = MagicMock()
    chunker.chunk.return_value = [
        {"content": "chunk1", "metadata": {"index": 0}},
        {"content": "chunk2", "metadata": {"index": 1}}
    ]

    embedding = AsyncMock()
    embedding.embed_batch.return_value = [[0.1, 0.2], [0.3, 0.4]]

    vector_store = AsyncMock()
    vector_store.add_documents.return_value = None
    vector_store.search.return_value = [
        {"content": "chunk1", "score": 0.9, "metadata": {"source": "test.md"}}
    ]

    llm_client = AsyncMock()
    llm_client.generate.return_value = "Test answer"

    return {
        "parser": parser,
        "chunker": chunker,
        "embedding": embedding,
        "vector_store": vector_store,
        "llm_client": llm_client
    }


@pytest.mark.asyncio
async def test_ingest_pipeline_integration(mock_components, tmp_path):
    """Test document ingestion pipeline."""
    pipeline = IngestPipeline(
        parser=mock_components["parser"],
        chunker=mock_components["chunker"],
        embedding=mock_components["embedding"],
        vector_store=mock_components["vector_store"]
    )

    test_file = tmp_path / "test.md"
    test_file.write_text("# Test\nContent")

    await pipeline.ingest_document(test_file)

    mock_components["parser"].parse.assert_called_once()
    mock_components["chunker"].chunk.assert_called_once()
    mock_components["embedding"].embed_batch.assert_called_once()
    mock_components["vector_store"].add_documents.assert_called_once()


@pytest.mark.asyncio
async def test_agent_orchestration_flow(mock_components):
    """Test complete agent orchestration flow."""
    retriever = RetrieverAgent(
        agent_id="retriever",
        config={
            "vector_store": mock_components["vector_store"],
            "embedding": mock_components["embedding"]
        }
    )

    analyzer = AnalyzerAgent(
        agent_id="analyzer",
        config={"llm_client": mock_components["llm_client"]}
    )

    orchestrator = OrchestratorAgent(
        agent_id="orchestrator",
        config={"retriever": retriever, "analyzer": analyzer}
    )

    query_msg = Message.create_request(
        from_agent="user",
        to_agent="orchestrator",
        intent="query",
        payload={"query": "What is Python GIL?"}
    )

    response = await orchestrator.process(query_msg)

    assert response.payload.get("answer") == "Test answer"
    mock_components["vector_store"].search.assert_called_once()
    mock_components["llm_client"].generate.assert_called_once()


@pytest.mark.asyncio
async def test_end_to_end_workflow(mock_components, tmp_path):
    """Test end-to-end: ingest -> query -> answer."""
    # Setup pipeline
    pipeline = IngestPipeline(
        parser=mock_components["parser"],
        chunker=mock_components["chunker"],
        embedding=mock_components["embedding"],
        vector_store=mock_components["vector_store"]
    )

    # Ingest document
    test_file = tmp_path / "python.md"
    test_file.write_text("# Python GIL\nGlobal Interpreter Lock")
    await pipeline.ingest_document(test_file)

    # Setup agents
    retriever = RetrieverAgent(
        agent_id="retriever",
        config={
            "vector_store": mock_components["vector_store"],
            "embedding": mock_components["embedding"]
        }
    )

    analyzer = AnalyzerAgent(
        agent_id="analyzer",
        config={"llm_client": mock_components["llm_client"]}
    )

    orchestrator = OrchestratorAgent(
        agent_id="orchestrator",
        config={"retriever": retriever, "analyzer": analyzer}
    )

    # Query
    query_msg = Message.create_request(
        from_agent="user",
        to_agent="orchestrator",
        intent="query",
        payload={"query": "What is GIL?"}
    )

    response = await orchestrator.process(query_msg)

    assert "answer" in response.payload
    assert response.message_type == "response"
