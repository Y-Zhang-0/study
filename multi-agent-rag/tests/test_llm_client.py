import pytest
from unittest.mock import Mock, patch, AsyncMock
from anthropic import Anthropic
from anthropic.types import Message as AnthropicMessage, ContentBlock, TextBlock, Usage

from src.infrastructure.llm_client import LLMClient, LLMConfig


@pytest.fixture
def llm_config():
    """LLM 配置 fixture"""
    return LLMConfig(
        api_key="test-api-key",
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        temperature=0.7,
    )


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic 客户端"""
    with patch("src.infrastructure.llm_client.Anthropic") as mock:
        yield mock


@pytest.fixture
def llm_client(llm_config, mock_anthropic_client):
    """LLM 客户端 fixture"""
    return LLMClient(llm_config)


class TestLLMConfig:
    """测试 LLMConfig"""

    def test_default_config(self):
        """测试默认配置"""
        config = LLMConfig(api_key="test-key")
        assert config.api_key == "test-key"
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.max_tokens == 4096
        assert config.temperature == 1.0

    def test_custom_config(self, llm_config):
        """测试自定义配置"""
        assert llm_config.api_key == "test-api-key"
        assert llm_config.model == "claude-3-5-sonnet-20241022"
        assert llm_config.max_tokens == 1024
        assert llm_config.temperature == 0.7


class TestLLMClient:
    """测试 LLMClient"""

    def test_client_initialization(self, llm_client, mock_anthropic_client):
        """测试客户端初始化"""
        mock_anthropic_client.assert_called_once_with(api_key="test-api-key")
        assert llm_client.config.model == "claude-3-5-sonnet-20241022"

    def test_generate_success(self, llm_client, mock_anthropic_client):
        """测试成功生成响应"""
        mock_response = AnthropicMessage(
            id="msg_123",
            type="message",
            role="assistant",
            content=[TextBlock(type="text", text="这是测试响应")],
            model="claude-3-5-sonnet-20241022",
            stop_reason="end_turn",
            usage=Usage(input_tokens=10, output_tokens=20),
        )

        mock_client_instance = mock_anthropic_client.return_value
        mock_client_instance.messages.create.return_value = mock_response

        result = llm_client.generate("测试提示词")

        assert result == "这是测试响应"
        mock_client_instance.messages.create.assert_called_once_with(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            temperature=0.7,
            messages=[{"role": "user", "content": "测试提示词"}],
        )

    def test_generate_with_system_prompt(self, llm_client, mock_anthropic_client):
        """测试带系统提示词的生成"""
        mock_response = AnthropicMessage(
            id="msg_124",
            type="message",
            role="assistant",
            content=[TextBlock(type="text", text="系统响应")],
            model="claude-3-5-sonnet-20241022",
            stop_reason="end_turn",
            usage=Usage(input_tokens=15, output_tokens=25),
        )

        mock_client_instance = mock_anthropic_client.return_value
        mock_client_instance.messages.create.return_value = mock_response

        result = llm_client.generate("用户提示", system="系统提示")

        assert result == "系统响应"
        mock_client_instance.messages.create.assert_called_once_with(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            temperature=0.7,
            messages=[{"role": "user", "content": "用户提示"}],
            system="系统提示",
        )

    def test_generate_api_error(self, llm_client, mock_anthropic_client):
        """测试 API 错误处理"""
        mock_client_instance = mock_anthropic_client.return_value
        mock_client_instance.messages.create.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            llm_client.generate("测试提示词")

