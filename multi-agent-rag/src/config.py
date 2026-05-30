# src/config.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    # Claude API
    anthropic_api_key: str

    # ChromaDB
    chroma_persist_dir: Path = Path("./data/chroma")

    # Embedding
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"

    # RAG
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k: int = 5

    # LLM
    llm_model: str = "claude-3-5-sonnet-20241022"
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# 全局配置实例 - 延迟初始化
_settings = None


def get_settings() -> Settings:
    """获取全局配置实例（延迟加载）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# 便捷访问函数
settings = get_settings
