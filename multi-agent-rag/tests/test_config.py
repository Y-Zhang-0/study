# tests/test_config.py
import os
import pytest

# 在导入 Settings 前设置默认环境变量
os.environ.setdefault("ANTHROPIC_API_KEY", "test-default-key")

from pathlib import Path
from src.config import Settings


def test_settings_from_env(tmp_path, monkeypatch):
    """测试从环境变量加载配置"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
    monkeypatch.setenv("CHUNK_SIZE", "256")

    settings = Settings()

    assert settings.anthropic_api_key == "test-key-123"
    assert settings.chunk_size == 256


def test_settings_defaults():
    """测试默认配置值"""
    settings = Settings(anthropic_api_key="test-key")

    assert settings.chunk_size == 512
    assert settings.chunk_overlap == 64
    assert settings.top_k == 5
    assert settings.llm_model == "claude-3-5-sonnet-20241022"
