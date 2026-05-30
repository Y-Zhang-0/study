from typing import Callable, Dict, List
from src.infrastructure.message import Message

MessageHandler = Callable[[Message], Message]


class MessageBus:
    """消息总线，负责消息路由和分发"""

    def __init__(self):
        self._handlers: Dict[str, Dict[str, MessageHandler]] = {}

    def register(self, agent_id: str, intent: str, handler: MessageHandler) -> None:
        """注册消息处理器"""
        if agent_id not in self._handlers:
            self._handlers[agent_id] = {}
        self._handlers[agent_id][intent] = handler

    def unregister(self, agent_id: str, intent: str) -> None:
        """注销消息处理器"""
        if agent_id in self._handlers and intent in self._handlers[agent_id]:
            del self._handlers[agent_id][intent]
            if not self._handlers[agent_id]:
                del self._handlers[agent_id]

    def send(self, message: Message) -> Message:
        """发送消息到指定 agent"""
        agent_id = message.to_agent
        intent = message.intent

        if agent_id not in self._handlers or intent not in self._handlers[agent_id]:
            raise ValueError(
                f"No handler registered for agent '{agent_id}' with intent '{intent}'"
            )

        handler = self._handlers[agent_id][intent]
        return handler(message)

    def broadcast(self, message: Message) -> List[Message]:
        """广播消息到所有注册了该 intent 的 agent"""
        intent = message.intent
        responses = []

        for agent_id, intents in self._handlers.items():
            if intent in intents:
                handler = intents[intent]
                response = handler(message)
                responses.append(response)

        return responses
