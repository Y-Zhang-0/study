import pytest
from unittest.mock import Mock, AsyncMock
from src.agents.analyzer import AnalyzerAgent
from src.infrastructure.message import Message


@pytest.mark.asyncio
async def test_analyzer_handle_analyze():
    """测试 Analyzer 处理分析请求"""
    mock_llm = Mock()
    mock_llm.call = AsyncMock(return_value="这是分析结果")

    agent = AnalyzerAgent(agent_id="analyzer")
    agent.llm_client = mock_llm

    msg = Message.create_request(
        from_agent="orchestrator",
        to_agent="analyzer",
        intent="analyze",
        payload={
            "intent": "analyze",
            "query": "什么是Python?",
            "chunks": [{"text": "Python是一门编程语言", "metadata": {}}],
        },
    )

    response = await agent.process(msg)

    assert response is not None
    assert "answer" in response.payload
    assert response.payload["answer"] == "这是分析结果"
