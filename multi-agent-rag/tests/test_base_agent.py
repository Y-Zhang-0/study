"""Tests for BaseAgent abstract class."""
import pytest
from abc import ABC
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent
from src.infrastructure.message import Message, MessageType


class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing."""

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.process_called = False
        self.last_message = None

    async def process(self, message: Message) -> Message:
        """Test implementation of process."""
        self.process_called = True
        self.last_message = message
        return Message.create_response(
            request=message,
            from_agent=self.agent_id,
            payload={"result": f"Processed: {message.payload.get('query', '')}"}
        )


class TestBaseAgent:
    """Test cases for BaseAgent."""

    def test_base_agent_is_abstract(self):
        """Test that BaseAgent cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent("test_agent")

    def test_concrete_agent_initialization(self):
        """Test concrete agent initialization."""
        agent = ConcreteAgent("agent_1")
        assert agent.agent_id == "agent_1"
        assert agent.config == {}
        assert agent.state == "idle"

    def test_agent_with_config(self):
        """Test agent initialization with config."""
        config = {"model": "gpt-4", "temperature": 0.7}
        agent = ConcreteAgent("agent_2", config)
        assert agent.agent_id == "agent_2"
        assert agent.config == config
        assert agent.state == "idle"

    @pytest.mark.asyncio
    async def test_process_message(self):
        """Test processing a message."""
        agent = ConcreteAgent("agent_1")
        message = Message.create_request(
            from_agent="user",
            to_agent="agent_1",
            intent="query",
            payload={"query": "test message"}
        )

        response = await agent.process(message)

        assert agent.process_called is True
        assert agent.last_message == message
        assert response.from_agent == "agent_1"
        assert response.to_agent == "user"
        assert response.type == MessageType.RESPONSE
        assert "Processed: test message" in response.payload["result"]

    def test_get_state(self):
        """Test getting agent state."""
        agent = ConcreteAgent("agent_1")
        assert agent.get_state() == "idle"

    def test_set_state(self):
        """Test setting agent state."""
        agent = ConcreteAgent("agent_1")
        agent.set_state("processing")
        assert agent.state == "processing"
        assert agent.get_state() == "processing"

    def test_get_info(self):
        """Test getting agent info."""
        config = {"model": "gpt-4"}
        agent = ConcreteAgent("agent_1", config)
        agent.set_state("processing")

        info = agent.get_info()

        assert info["agent_id"] == "agent_1"
        assert info["state"] == "processing"
        assert info["config"] == config

    def test_abstract_process_method(self):
        """Test that process method must be implemented."""
        class IncompleteAgent(BaseAgent):
            pass

        with pytest.raises(TypeError):
            IncompleteAgent("incomplete")

