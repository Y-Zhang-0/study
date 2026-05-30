from typing import Optional
from pydantic import BaseModel
from anthropic import Anthropic


class LLMConfig(BaseModel):
    """LLM 配置"""

    api_key: str
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 1.0


class LLMClient:
    """LLM 客户端，封装 Anthropic SDK"""

    def __init__(self, config: LLMConfig):
        """初始化 LLM 客户端

        Args:
            config: LLM 配置
        """
        self.config = config
        self.client = Anthropic(api_key=config.api_key)

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """生成响应

        Args:
            prompt: 用户提示词
            system: 系统提示词（可选）

        Returns:
            生成的文本响应

        Raises:
            Exception: API 调用失败时抛出异常
        """
        kwargs = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        return response.content[0].text
