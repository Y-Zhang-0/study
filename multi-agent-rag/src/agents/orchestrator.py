"""Orchestrator Agent for routing requests."""
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent
from src.infrastructure.message import Message


class OrchestratorAgent(BaseAgent):
    """协调器 Agent，负责路由请求"""

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.retriever = config.get("retriever") if config else None
        self.analyzer = config.get("analyzer") if config else None

    async def process(self, message: Message) -> Message:
        """处理用户查询，协调 retriever 和 analyzer"""
        query = message.payload.get("query", "")

        if not query or not query.strip():
            return Message.create_response(
                request=message,
                from_agent=self.agent_id,
                payload={"error": "Empty query"}
            )

        retrieval_msg = Message.create_request(
            from_agent=self.agent_id,
            to_agent="retriever",
            intent="retrieve",
            payload={"query": query}
        )
        retrieval_response = await self.retriever.process(retrieval_msg)

        analysis_msg = Message.create_request(
            from_agent=self.agent_id,
            to_agent="analyzer",
            intent="analyze",
            payload={
                "query": query,
                "chunks": retrieval_response.payload.get("documents", [])
            }
        )
        analysis_response = await self.analyzer.process(analysis_msg)

        return Message.create_response(
            request=message,
            from_agent=self.agent_id,
            payload={"answer": analysis_response.payload.get("answer")}
        )
