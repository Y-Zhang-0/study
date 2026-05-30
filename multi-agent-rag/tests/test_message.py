import pytest
from src.infrastructure.message import Message, MessageType


def test_create_request_message():
    """测试创建 REQUEST 消息"""
    msg = Message.create_request(
        from_agent="orchestrator",
        to_agent="retriever",
        intent="retrieve",
        payload={"query": "test", "top_k": 5}
    )

    assert msg.type == MessageType.REQUEST
    assert msg.from_agent == "orchestrator"
    assert msg.to_agent == "retriever"
    assert msg.intent == "retrieve"
    assert msg.payload["query"] == "test"
    assert msg.id is not None
    assert msg.parent_id is None


def test_create_response_message():
    """测试创建 RESPONSE 消息"""
    request = Message.create_request(
        from_agent="orchestrator",
        to_agent="retriever",
        intent="retrieve",
        payload={}
    )

    response = Message.create_response(
        request=request,
        from_agent="retriever",
        payload={"chunks": ["chunk1", "chunk2"]}
    )

    assert response.type == MessageType.RESPONSE
    assert response.from_agent == "retriever"
    assert response.to_agent == "orchestrator"
    assert response.parent_id == request.id
    assert len(response.payload["chunks"]) == 2
