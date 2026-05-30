from enum import Enum
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """消息类型"""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"


class Message(BaseModel):
    """消息协议"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    from_agent: str
    to_agent: str
    type: MessageType
    intent: str
    payload: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    parent_id: Optional[str] = None

    @classmethod
    def create_request(
        cls,
        from_agent: str,
        to_agent: str,
        intent: str,
        payload: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> "Message":
        """创建 REQUEST 消息"""
        return cls(
            from_agent=from_agent,
            to_agent=to_agent,
            type=MessageType.REQUEST,
            intent=intent,
            payload=payload,
            context=context or {},
        )

    @classmethod
    def create_response(
        cls,
        request: "Message",
        from_agent: str,
        payload: dict[str, Any],
    ) -> "Message":
        """创建 RESPONSE 消息"""
        return cls(
            from_agent=from_agent,
            to_agent=request.from_agent,
            type=MessageType.RESPONSE,
            intent=request.intent,
            payload=payload,
            context=request.context,
            parent_id=request.id,
        )
