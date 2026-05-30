from typing import Dict, Any, Optional
from src.agents.base import BaseAgent
from src.infrastructure.message import Message


class AnalyzerAgent(BaseAgent):
    """分析 Agent"""

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.llm_client = None

    async def process(self, message: Message) -> Message:
        """处理消息"""
        intent = message.payload.get("intent", "")

        if intent == "analyze":
            return await self._handle_analyze(message)
        elif intent == "summarize":
            return await self._handle_summarize(message)

        return Message.create_response(
            request=message,
            from_agent=self.agent_id,
            payload={"error": "Unknown intent"}
        )

    async def _handle_analyze(self, message: Message) -> Message:
        """处理分析请求"""
        query = message.payload.get("query", "")
        chunks = message.payload.get("chunks", [])

        context = "\n\n".join([f"文档片段 {i+1}:\n{c['text']}" for i, c in enumerate(chunks)])

        prompt = f"""基于以下文档片段回答问题。

问题: {query}

文档片段:
{context}

请基于文档内容给出准确的回答。如果文档中没有相关信息,请说明。"""

        answer = await self.llm_client.call(prompt)

        return Message.create_response(
            request=message,
            from_agent=self.agent_id,
            payload={"answer": answer},
        )

    async def _handle_summarize(self, message: Message) -> Message:
        """处理总结请求"""
        text = message.payload.get("text", "")

        prompt = f"请总结以下内容:\n\n{text}"
        summary = await self.llm_client.call(prompt)

        return Message.create_response(
            request=message,
            from_agent=self.agent_id,
            payload={"summary": summary},
        )
