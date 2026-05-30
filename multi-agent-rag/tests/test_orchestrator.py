"""Tests for Orchestrator Agent."""
import pytest
from unittest.mock import Mock, AsyncMock
from src.agents.orchestrator import OrchestratorAgent
from src.infrastructure.message import Message


@pytest.fixture
def mock_retriever():
    """Mock retriever agent."""
    agent = Mock()

    async def mock_process(msg):
        return Message.create_response(
            request=msg,
            from_agent="retriever",
            payload={"documents": [{"content": "doc1"}]}
        )

    agent.process = AsyncMock(side_effect=mock_process)
    return agent


@pytest.fixture
def mock_analyzer():
    """Mock analyzer agent."""
    agent = Mock()

    async def mock_process(msg):
        return Message.create_response(
            request=msg,
            from_agent="analyzer",
            payload={"answer": "test answer"}
        )

    agent.process = AsyncMock(side_effect=mock_process)
    return agent


@pytest.fixture
def orchestrator(mock_retriever, mock_analyzer):
    """Create orchestrator with mock agents."""
    config = {
        "retriever": mock_retriever,
        "analyzer": mock_analyzer
    }
    return OrchestratorAgent("orchestrator", config)


@pytest.mark.asyncio
async def test_orchestrator_routes_query(orchestrator, mock_retriever, mock_analyzer):
    """Test orchestrator routes user query through retriever and analyzer."""
    message = Message.create_request(
        from_agent="user",
        to_agent="orchestrator",
        intent="query",
        payload={"query": "What is RAG?"}
    )

    response = await orchestrator.process(message)

    assert response.payload.get("answer") == "test answer"
    mock_retriever.process.assert_called_once()
    mock_analyzer.process.assert_called_once()


@pytest.mark.asyncio
async def test_orchestrator_handles_empty_query(orchestrator):
    """Test orchestrator handles empty query."""
    message = Message.create_request(
        from_agent="user",
        to_agent="orchestrator",
        intent="query",
        payload={"query": ""}
    )

    response = await orchestrator.process(message)

    assert "error" in response.payload
