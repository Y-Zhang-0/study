"""Base class for all agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.infrastructure.message import Message


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize agent.

        Args:
            agent_id: Unique identifier for the agent
            config: Optional configuration dictionary
        """
        self.agent_id = agent_id
        self.config = config or {}
        self.state = "idle"

    @abstractmethod
    async def process(self, message: Message) -> Message:
        """Process incoming message and return response.

        Args:
            message: Incoming message to process

        Returns:
            Response message

        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        pass

    def get_state(self) -> str:
        """Get current agent state.

        Returns:
            Current state string
        """
        return self.state

    def set_state(self, state: str) -> None:
        """Set agent state.

        Args:
            state: New state string
        """
        self.state = state

    def get_info(self) -> Dict[str, Any]:
        """Get agent information.

        Returns:
            Dictionary containing agent_id, state, and config
        """
        return {
            "agent_id": self.agent_id,
            "state": self.state,
            "config": self.config
        }

