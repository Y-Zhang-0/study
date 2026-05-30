"""Tests for Retriever Agent."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.agents.retriever import RetrieverAgent
from src.infrastructure.message import Message


@pytest.fixture
def mock_vector_store():
    """Mock vector store."""
    store = Mock()
    store.search = AsyncMock(return_value=[
        {"content": "Test doc 1", "metadata": {"source": "test1.md"}, "score": 0.9},
        {"content": "Test doc 2", "metadata": {"source": "test2.md"}, "score": 0.8}
    ])
    return store


@pytest.fixture
def retriever_agent(mock_vector_store):
    """Create retriever agent with mock store."""
    config = {"collection_name": "test_collection", "top_k": 5}
    agent = RetrieverAgent("retriever-1", config)
    agent.vector_store = mock_vector_store
    return agent


@pytest.mark.asyncio
async def test_retriever_process_query(retriever_agent, mock_vector_store):
    """Test retriever processes query message."""
    message = Message.create_request(
        from_agent="orchestrator",
        to_agent="retriever-1",
        intent="retrieve",
        payload={"query": "What is RAG?"}
    )

    response = await retriever_agent.process(message)

    assert response.intent == "retrieve"
    assert "documents" in response.payload
    assert len(response.payload["documents"]) == 2
    mock_vector_store.search.assert_called_once()


@pytest.mark.asyncio
async def test_retriever_empty_query(retriever_agent):
    """Test retriever handles empty query."""
    message = Message.create_request(
        from_agent="orchestrator",
        to_agent="retriever-1",
        intent="retrieve",
        payload={"query": ""}
    )

    response = await retriever_agent.process(message)

    assert "error" in response.payload
