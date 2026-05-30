import pytest
from src.infrastructure.message import Message, MessageType
from src.infrastructure.message_bus import MessageBus, MessageHandler


class TestMessageBus:
    """MessageBus 测试套件"""

    def test_register_handler(self):
        """测试注册处理器"""
        bus = MessageBus()
        handler_called = False

        def handler(msg: Message) -> Message:
            nonlocal handler_called
            handler_called = True
            return Message.create_response(msg, "agent_b", {"result": "ok"})

        bus.register("agent_b", "query", handler)

        msg = Message.create_request(
            from_agent="agent_a",
            to_agent="agent_b",
            intent="query",
            payload={"q": "test"}
        )

        response = bus.send(msg)
        assert handler_called
        assert response.type == MessageType.RESPONSE
        assert response.payload["result"] == "ok"

    def test_unregister_handler(self):
        """测试注销处理器"""
        bus = MessageBus()

        def handler(msg: Message) -> Message:
            return Message.create_response(msg, "agent_b", {"result": "ok"})

        bus.register("agent_b", "query", handler)
        bus.unregister("agent_b", "query")

        msg = Message.create_request(
            from_agent="agent_a",
            to_agent="agent_b",
            intent="query",
            payload={"q": "test"}
        )

        with pytest.raises(ValueError, match="No handler registered"):
            bus.send(msg)

    def test_send_message_no_handler(self):
        """测试发送消息但无处理器"""
        bus = MessageBus()

        msg = Message.create_request(
            from_agent="agent_a",
            to_agent="agent_b",
            intent="query",
            payload={"q": "test"}
        )

        with pytest.raises(ValueError, match="No handler registered"):
            bus.send(msg)

    def test_broadcast_message(self):
        """测试广播消息"""
        bus = MessageBus()
        handlers_called = []

        def handler_b(msg: Message) -> Message:
            handlers_called.append("agent_b")
            return Message.create_response(msg, "agent_b", {"result": "ok_b"})

        def handler_c(msg: Message) -> Message:
            handlers_called.append("agent_c")
            return Message.create_response(msg, "agent_c", {"result": "ok_c"})

        bus.register("agent_b", "event", handler_b)
        bus.register("agent_c", "event", handler_c)

        msg = Message(
            from_agent="agent_a",
            to_agent="*",
            type=MessageType.EVENT,
            intent="event",
            payload={"data": "test"}
        )

        responses = bus.broadcast(msg)
        assert len(responses) == 2
        assert "agent_b" in handlers_called
        assert "agent_c" in handlers_called

    def test_handler_exception(self):
        """测试处理器异常"""
        bus = MessageBus()

        def failing_handler(msg: Message) -> Message:
            raise RuntimeError("Handler error")

        bus.register("agent_b", "query", failing_handler)

        msg = Message.create_request(
            from_agent="agent_a",
            to_agent="agent_b",
            intent="query",
            payload={"q": "test"}
        )

        with pytest.raises(RuntimeError, match="Handler error"):
            bus.send(msg)

    def test_multiple_intents_same_agent(self):
        """测试同一 agent 注册多个 intent"""
        bus = MessageBus()
        query_called = False
        update_called = False

        def query_handler(msg: Message) -> Message:
            nonlocal query_called
            query_called = True
            return Message.create_response(msg, "agent_b", {"result": "query_ok"})

        def update_handler(msg: Message) -> Message:
            nonlocal update_called
            update_called = True
            return Message.create_response(msg, "agent_b", {"result": "update_ok"})

        bus.register("agent_b", "query", query_handler)
        bus.register("agent_b", "update", update_handler)

        msg1 = Message.create_request(
            from_agent="agent_a",
            to_agent="agent_b",
            intent="query",
            payload={"q": "test"}
        )
        response1 = bus.send(msg1)
        assert query_called
        assert not update_called

        msg2 = Message.create_request(
            from_agent="agent_a",
            to_agent="agent_b",
            intent="update",
            payload={"data": "new"}
        )
        response2 = bus.send(msg2)
        assert update_called
        assert response2.payload["result"] == "update_ok"


