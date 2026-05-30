"""Retriever Agent for document retrieval."""
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent
from src.infrastructure.message import Message


class RetrieverAgent(BaseAgent):
    """Agent responsible for retrieving relevant documents."""

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.vector_store = None
        self.top_k = config.get("top_k", 5) if config else 5

    async def process(self, message: Message) -> Message:
        """Process retrieval query."""
        query = message.payload.get("query", "")

        if not query or not query.strip():
            return Message.create_response(
                request=message,
                from_agent=self.agent_id,
                payload={"error": "Empty query"}
            )

        results = await self.vector_store.search(query, top_k=self.top_k)

        return Message.create_response(
            request=message,
            from_agent=self.agent_id,
            payload={"documents": results, "query": query}
        )
