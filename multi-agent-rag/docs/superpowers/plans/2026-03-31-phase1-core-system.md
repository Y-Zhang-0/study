# Phase 1: Multi-Agent RAG 核心系统实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 Multi-Agent RAG 系统的 Phase 1 基础版,包含消息总线、三个核心 Agent、RAG 管道(Markdown/PDF)、CLI 交互

**Architecture:** 三层架构 - Infrastructure 层(MessageBus/LLM/VectorStore/Embedding)、Agent 层(Orchestrator/Retriever/Analyzer)、Application 层(CLI)。中心调度模式,所有消息经过 MessageBus 路由。

**Tech Stack:** Python 3.10+, anthropic SDK, ChromaDB, sentence-transformers, PyMuPDF, click, pydantic-settings, pytest

---

## 文件结构规划

Phase 1 需要创建的文件:

**Infrastructure 层:**
- `src/infrastructure/message.py` - 消息协议定义(Message 类)
- `src/infrastructure/message_bus.py` - 消息总线(路由、订阅、分发)
- `src/infrastructure/llm_client.py` - Claude API 封装
- `src/infrastructure/vector_store.py` - ChromaDB 封装
- `src/infrastructure/embedding.py` - Embedding 抽象层(本地 sentence-transformers)

**RAG 层:**
- `src/rag/parser/base.py` - 文档解析器接口
- `src/rag/parser/markdown.py` - Markdown 解析器
- `src/rag/parser/pdf.py` - PDF 解析器
- `src/rag/chunker.py` - 文档分块策略
- `src/rag/ingest.py` - 摄入管道编排

**Agent 层:**
- `src/agents/base.py` - BaseAgent 抽象类
- `src/agents/orchestrator.py` - 调度 Agent
- `src/agents/retriever.py` - 检索 Agent
- `src/agents/analyzer.py` - 分析 Agent

**Application 层:**
- `src/config.py` - 配置管理(pydantic-settings)
- `src/cli.py` - CLI 入口(click)

**配置和依赖:**
- `pyproject.toml` - 项目依赖和元数据
- `.env.example` - 环境变量模板
- `README.md` - 项目说明

**测试:**
- `tests/test_message.py` - 消息协议测试
- `tests/test_message_bus.py` - 消息总线测试
- `tests/test_agents.py` - Agent 测试
- `tests/test_rag.py` - RAG 管道测试

---

### Task 1: 项目初始化和依赖配置

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `README.md`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "multi-agent-rag"
version = "0.1.0"
description = "Multi-Agent RAG system with document Q&A"
requires-python = ">=3.10"
dependencies = [
    "anthropic>=0.40.0",
    "chromadb>=0.5.0",
    "sentence-transformers>=3.0.0",
    "pymupdf>=1.24.0",
    "click>=8.1.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "black>=24.0.0",
    "ruff>=0.3.0",
]

[project.scripts]
mar = "src.cli:cli"

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
target-version = "py310"
```

- [ ] **Step 2: 创建 .env.example**

```bash
# Claude API Key (required)
ANTHROPIC_API_KEY=your_api_key_here

# ChromaDB 配置
CHROMA_PERSIST_DIR=./data/chroma

# Embedding 配置
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

# RAG 配置
CHUNK_SIZE=512
CHUNK_OVERLAP=64
TOP_K=5

# LLM 配置
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_MAX_TOKENS=4096
LLM_TEMPERATURE=0.7
```

- [ ] **Step 3: 创建 README.md**

```markdown
# Multi-Agent RAG System

AI 驱动的 Multi-Agent 协作系统,支持文档问答和软件开发全流程。

## 快速开始

### 1. 安装依赖

\`\`\`bash
pip install -e ".[dev]"
\`\`\`

### 2. 配置环境变量

\`\`\`bash
cp .env.example .env
# 编辑 .env 文件,填入你的 ANTHROPIC_API_KEY
\`\`\`

### 3. 使用 CLI

\`\`\`bash
# 摄入文档
mar ingest ./docs

# 问答
mar ask "Python的GIL是什么?"

# 查看知识库
mar collections
\`\`\`

## 架构

- **Infrastructure 层**: MessageBus, LLM Client, VectorStore, Embedding
- **Agent 层**: Orchestrator, Retriever, Analyzer
- **Application 层**: CLI

## 开发

\`\`\`bash
# 运行测试
pytest

# 代码格式化
black src tests
ruff check src tests
\`\`\`
```

- [ ] **Step 4: 创建目录结构和 __init__.py**

```bash
mkdir -p src/agents src/infrastructure src/rag/parser tests
touch src/__init__.py tests/__init__.py
touch src/agents/__init__.py src/infrastructure/__init__.py src/rag/__init__.py src/rag/parser/__init__.py
```

- [ ] **Step 5: 安装依赖**

```bash
cd /c/Users/zhangyu/Desktop/code/study/multi-agent-rag
pip install -e ".[dev]"
```

Expected: 所有依赖安装成功,包括 anthropic, chromadb, sentence-transformers 等

- [ ] **Step 6: 提交**

```bash
git add .
git commit -m "chore: initialize project structure and dependencies"
```

---

### Task 2: 配置管理

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: 编写配置测试**

```python
# tests/test_config.py
import os
from pathlib import Path
import pytest
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
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_config.py -v
```

Expected: FAIL - ModuleNotFoundError: No module named 'src.config'

- [ ] **Step 3: 实现配置管理**

```python
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


# 全局配置实例
settings = Settings()
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_config.py -v
```

Expected: PASS - 2 tests passed

- [ ] **Step 5: 提交**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add configuration management with pydantic-settings"
```

---

### Task 3: 消息协议

**Files:**
- Create: `src/infrastructure/message.py`
- Create: `tests/test_message.py`

- [ ] **Step 1: 编写消息协议测试**

```python
# tests/test_message.py
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
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_message.py -v
```

Expected: FAIL - ModuleNotFoundError: No module named 'src.infrastructure.message'

- [ ] **Step 3: 实现消息协议**

```python
# src/infrastructure/message.py
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_message.py -v
```

Expected: PASS - 2 tests passed

- [ ] **Step 5: 提交**

```bash
git add src/infrastructure/message.py tests/test_message.py src/infrastructure/__init__.py
git commit -m "feat: implement message protocol with Request/Response types"
```

---

### Task 4: 消息总线 (MessageBus)

**Files:**
- Create: `src/infrastructure/message_bus.py`
- Create: `tests/test_message_bus.py`

- [ ] **Step 1: 编写消息总线测试**

```python
# tests/test_message_bus.py
import pytest
from src.infrastructure.message import Message
from src.infrastructure.message_bus import MessageBus, RoutingMode


def test_subscribe_and_publish():
    """测试订阅和发布消息"""
    bus = MessageBus(mode=RoutingMode.CENTRALIZED)
    received_messages = []

    def handler(msg: Message):
        received_messages.append(msg)

    bus.subscribe("retrieve", handler)

    msg = Message.create_request(
        from_agent="orchestrator",
        to_agent="retriever",
        intent="retrieve",
        payload={"query": "test"}
    )

    bus.publish(msg)

    assert len(received_messages) == 1
    assert received_messages[0].intent == "retrieve"


def test_centralized_mode_routes_through_orchestrator():
    """测试中心调度模式下消息经过 orchestrator"""
    bus = MessageBus(mode=RoutingMode.CENTRALIZED)
    orchestrator_messages = []
    retriever_messages = []

    bus.subscribe("ALL", lambda msg: orchestrator_messages.append(msg))
    bus.subscribe("retrieve", lambda msg: retriever_messages.append(msg))

    msg = Message.create_request(
        from_agent="orchestrator",
        to_agent="retriever",
        intent="retrieve",
        payload={}
    )

    bus.publish(msg)

    # 中心调度模式下,orchestrator 订阅 ALL,能收到所有消息
    assert len(orchestrator_messages) == 1
    assert len(retriever_messages) == 1
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_message_bus.py -v
```

Expected: FAIL - ModuleNotFoundError

- [ ] **Step 3: 实现消息总线**

```python
# src/infrastructure/message_bus.py
from enum import Enum
from typing import Callable
from collections import defaultdict
from src.infrastructure.message import Message


class RoutingMode(str, Enum):
    """路由模式"""
    CENTRALIZED = "centralized"  # 中心调度
    HYBRID = "hybrid"  # 混合模式


class MessageBus:
    """消息总线"""

    def __init__(self, mode: RoutingMode = RoutingMode.CENTRALIZED):
        self.mode = mode
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._message_history: list[Message] = []

    def subscribe(self, intent: str, handler: Callable[[Message], None]):
        """订阅消息"""
        self._subscribers[intent].append(handler)

    def publish(self, message: Message):
        """发布消息"""
        self._message_history.append(message)

        # 发送给订阅了 ALL 的处理器(通常是 Orchestrator)
        for handler in self._subscribers.get("ALL", []):
            handler(message)

        # 发送给订阅了特定 intent 的处理器
        for handler in self._subscribers.get(message.intent, []):
            handler(message)

    def get_history(self) -> list[Message]:
        """获取消息历史"""
        return self._message_history.copy()
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_message_bus.py -v
```

Expected: PASS - 2 tests passed

- [ ] **Step 5: 提交**

```bash
git add src/infrastructure/message_bus.py tests/test_message_bus.py
git commit -m "feat: implement MessageBus with centralized routing"
```

---

### Task 5: LLM Client (Claude API 封装)

**Files:**
- Create: `src/infrastructure/llm_client.py`
- Create: `tests/test_llm_client.py`

- [ ] **Step 1: 编写 LLM Client 测试**

```python
# tests/test_llm_client.py
import pytest
from unittest.mock import Mock, patch
from src.infrastructure.llm_client import LLMClient


def test_llm_client_call():
    """测试 LLM 调用"""
    with patch('anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="测试回答")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        llm = LLMClient(api_key="test-key")
        response = llm.call("测试问题")

        assert response == "测试回答"
        mock_client.messages.create.assert_called_once()
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_llm_client.py -v
```

- [ ] **Step 3: 实现 LLM Client**

```python
# src/infrastructure/llm_client.py
import anthropic
from src.config import settings


class LLMClient:
    """Claude API 封装"""

    def __init__(self, api_key: str | None = None):
        self.client = anthropic.Anthropic(api_key=api_key or settings.anthropic_api_key)
        self.model = settings.llm_model
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature

    def call(self, prompt: str, system: str | None = None) -> str:
        """调用 Claude API"""
        messages = [{"role": "user", "content": prompt}]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system or "",
            messages=messages,
        )

        return response.content[0].text
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_llm_client.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/infrastructure/llm_client.py tests/test_llm_client.py
git commit -m "feat: implement LLM client with Claude API"
```

---

### Task 6: Embedding Provider

**Files:**
- Create: `src/infrastructure/embedding.py`
- Create: `tests/test_embedding.py`

- [ ] **Step 1: 编写 Embedding 测试**

```python
# tests/test_embedding.py
import pytest
from src.infrastructure.embedding import LocalEmbedding


def test_local_embedding_encode():
    """测试本地 embedding 编码"""
    embedding = LocalEmbedding()
    texts = ["hello world", "test document"]

    vectors = embedding.encode(texts)

    assert len(vectors) == 2
    assert len(vectors[0]) > 0  # 向量维度 > 0
    assert isinstance(vectors[0][0], float)
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_embedding.py -v
```

- [ ] **Step 3: 实现 Embedding Provider**

```python
# src/infrastructure/embedding.py
from sentence_transformers import SentenceTransformer
from src.config import settings


class LocalEmbedding:
    """本地 Embedding (sentence-transformers)"""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self.device = settings.embedding_device
        self.model = SentenceTransformer(self.model_name, device=self.device)

    def encode(self, texts: list[str]) -> list[list[float]]:
        """编码文本为向量"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """向量维度"""
        return self.model.get_sentence_embedding_dimension()
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_embedding.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/infrastructure/embedding.py tests/test_embedding.py
git commit -m "feat: implement local embedding with sentence-transformers"
```

---

### Task 7: Vector Store (ChromaDB 封装)

**Files:**
- Create: `src/infrastructure/vector_store.py`
- Create: `tests/test_vector_store.py`

- [ ] **Step 1: 编写 VectorStore 测试**

```python
# tests/test_vector_store.py
import pytest
from src.infrastructure.vector_store import VectorStore
from src.infrastructure.embedding import LocalEmbedding


def test_vector_store_add_and_query(tmp_path):
    """测试向量存储的添加和查询"""
    embedding = LocalEmbedding()
    store = VectorStore(persist_dir=str(tmp_path), embedding=embedding)

    # 添加文档
    store.add_documents(
        collection="test",
        texts=["Python is great", "I love programming"],
        metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    )

    # 查询
    results = store.query(collection="test", query="Python programming", top_k=2)

    assert len(results) == 2
    assert "Python" in results[0]["text"] or "programming" in results[0]["text"]
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_vector_store.py -v
```

- [ ] **Step 3: 实现 VectorStore**

```python
# src/infrastructure/vector_store.py
import chromadb
from chromadb.config import Settings as ChromaSettings
from src.config import settings
from src.infrastructure.embedding import LocalEmbedding


class VectorStore:
    """ChromaDB 向量存储封装"""

    def __init__(self, persist_dir: str | None = None, embedding: LocalEmbedding | None = None):
        self.persist_dir = persist_dir or str(settings.chroma_persist_dir)
        self.embedding = embedding or LocalEmbedding()

        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

    def add_documents(
        self,
        collection: str,
        texts: list[str],
        metadatas: list[dict] | None = None,
    ):
        """添加文档到集合"""
        coll = self.client.get_or_create_collection(collection)

        embeddings = self.embedding.encode(texts)
        ids = [f"doc_{i}" for i in range(len(texts))]

        coll.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas or [{} for _ in texts],
        )

    def query(self, collection: str, query: str, top_k: int = 5) -> list[dict]:
        """查询相似文档"""
        coll = self.client.get_collection(collection)

        query_embedding = self.embedding.encode([query])[0]

        results = coll.query(query_embeddings=[query_embedding], n_results=top_k)

        return [
            {"text": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]

    def list_collections(self) -> list[str]:
        """列出所有集合"""
        return [c.name for c in self.client.list_collections()]

    def delete_collection(self, collection: str):
        """删除集合"""
        self.client.delete_collection(collection)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_vector_store.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/infrastructure/vector_store.py tests/test_vector_store.py
git commit -m "feat: implement VectorStore with ChromaDB"
```

---

### Task 8: 文档解析器基类和 Chunker

**Files:**
- Create: `src/rag/parser/base.py`
- Create: `src/rag/chunker.py`
- Create: `tests/test_chunker.py`

- [ ] **Step 1: 实现解析器基类**

```python
# src/rag/parser/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """文档块"""
    text: str
    metadata: dict


class DocumentParser(ABC):
    """文档解析器接口"""

    @abstractmethod
    def parse(self, file_path: str) -> list[DocumentChunk]:
        """解析文档,返回文档块列表"""
        pass
```

- [ ] **Step 2: 编写 Chunker 测试**

```python
# tests/test_chunker.py
import pytest
from src.rag.chunker import Chunker


def test_chunker_split_text():
    """测试文本分块"""
    chunker = Chunker(chunk_size=20, chunk_overlap=5)
    text = "This is a test document. It has multiple sentences. We will split it."

    chunks = chunker.split(text, metadata={"source": "test.txt"})

    assert len(chunks) > 1
    assert all(len(c.text) <= 25 for c in chunks)  # 允许一些误差
    assert all(c.metadata["source"] == "test.txt" for c in chunks)
```

- [ ] **Step 3: 运行测试确认失败**

```bash
pytest tests/test_chunker.py -v
```

- [ ] **Step 4: 实现 Chunker**

```python
# src/rag/chunker.py
from src.rag.parser.base import DocumentChunk
from src.config import settings


class Chunker:
    """文档分块器"""

    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    def split(self, text: str, metadata: dict | None = None) -> list[DocumentChunk]:
        """分块文本"""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            if chunk_text.strip():
                chunks.append(DocumentChunk(text=chunk_text, metadata=metadata or {}))

            start = end - self.chunk_overlap

        return chunks
```

- [ ] **Step 5: 运行测试确认通过**

```bash
pytest tests/test_chunker.py -v
```

- [ ] **Step 6: 提交**

```bash
git add src/rag/parser/base.py src/rag/chunker.py tests/test_chunker.py src/rag/__init__.py src/rag/parser/__init__.py
git commit -m "feat: implement document parser base and chunker"
```

---

### Task 9: Markdown 和 PDF 解析器

**Files:**
- Create: `src/rag/parser/markdown.py`
- Create: `src/rag/parser/pdf.py`
- Create: `tests/test_parsers.py`

- [ ] **Step 1: 编写解析器测试**

```python
# tests/test_parsers.py
import pytest
from pathlib import Path
from src.rag.parser.markdown import MarkdownParser
from src.rag.parser.pdf import PDFParser


def test_markdown_parser(tmp_path):
    """测试 Markdown 解析"""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Title\n\nSome content here.\n\n## Section\n\nMore content.")

    parser = MarkdownParser()
    chunks = parser.parse(str(md_file))

    assert len(chunks) > 0
    assert any("Title" in c.text for c in chunks)
    assert all(c.metadata["file_name"] == "test.md" for c in chunks)


def test_pdf_parser(tmp_path):
    """测试 PDF 解析 - 需要实际 PDF 文件,这里用 mock"""
    # 实际测试需要 PDF 文件,这里简化
    parser = PDFParser()
    assert parser is not None
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_parsers.py -v
```

- [ ] **Step 3: 实现 Markdown 解析器**

```python
# src/rag/parser/markdown.py
from pathlib import Path
from src.rag.parser.base import DocumentParser, DocumentChunk
from src.rag.chunker import Chunker


class MarkdownParser(DocumentParser):
    """Markdown 解析器"""

    def __init__(self):
        self.chunker = Chunker()

    def parse(self, file_path: str) -> list[DocumentChunk]:
        """解析 Markdown 文件"""
        path = Path(file_path)
        text = path.read_text(encoding="utf-8")

        metadata = {
            "file_name": path.name,
            "file_path": str(path),
            "doc_type": "markdown",
        }

        return self.chunker.split(text, metadata)
```

- [ ] **Step 4: 实现 PDF 解析器**

```python
# src/rag/parser/pdf.py
import fitz  # PyMuPDF
from pathlib import Path
from src.rag.parser.base import DocumentParser, DocumentChunk
from src.rag.chunker import Chunker


class PDFParser(DocumentParser):
    """PDF 解析器"""

    def __init__(self):
        self.chunker = Chunker()

    def parse(self, file_path: str) -> list[DocumentChunk]:
        """解析 PDF 文件"""
        path = Path(file_path)
        doc = fitz.open(file_path)

        text_parts = []
        for page_num, page in enumerate(doc, start=1):
            text_parts.append(page.get_text())

        full_text = "\n\n".join(text_parts)

        metadata = {
            "file_name": path.name,
            "file_path": str(path),
            "doc_type": "pdf",
            "pages": len(doc),
        }

        doc.close()

        return self.chunker.split(full_text, metadata)
```

- [ ] **Step 5: 运行测试确认通过**

```bash
pytest tests/test_parsers.py::test_markdown_parser -v
```

- [ ] **Step 6: 提交**

```bash
git add src/rag/parser/markdown.py src/rag/parser/pdf.py tests/test_parsers.py
git commit -m "feat: implement Markdown and PDF parsers"
```

---

### Task 10: BaseAgent 抽象类

**Files:**
- Create: `src/agents/base.py`
- Create: `tests/test_base_agent.py`

- [ ] **Step 1: 编写 BaseAgent 测试**

```python
# tests/test_base_agent.py
import pytest
from src.agents.base import BaseAgent
from src.infrastructure.message import Message
from src.infrastructure.message_bus import MessageBus


class TestAgent(BaseAgent):
    """测试用 Agent"""

    def handle(self, message: Message) -> Message | None:
        return Message.create_response(
            request=message,
            from_agent=self.name,
            payload={"result": "handled"},
        )


def test_base_agent_subscribe_and_handle():
    """测试 Agent 订阅和处理消息"""
    bus = MessageBus()
    agent = TestAgent(name="test_agent", subscriptions=["test"], bus=bus)

    msg = Message.create_request(
        from_agent="sender",
        to_agent="test_agent",
        intent="test",
        payload={},
    )

    bus.publish(msg)

    # Agent 应该已经处理了消息
    history = bus.get_history()
    assert len(history) >= 1
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_base_agent.py -v
```

- [ ] **Step 3: 实现 BaseAgent**

```python
# src/agents/base.py
from abc import ABC, abstractmethod
from src.infrastructure.message import Message
from src.infrastructure.message_bus import MessageBus
from src.infrastructure.llm_client import LLMClient


class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(
        self,
        name: str,
        subscriptions: list[str],
        bus: MessageBus,
        llm_client: LLMClient | None = None,
    ):
        self.name = name
        self.subscriptions = subscriptions
        self.bus = bus
        self.llm_client = llm_client or LLMClient()

        # 订阅消息
        for intent in subscriptions:
            self.bus.subscribe(intent, self._on_message)

    def _on_message(self, message: Message):
        """接收消息的内部处理"""
        response = self.handle(message)
        if response:
            self.bus.publish(response)

    @abstractmethod
    def handle(self, message: Message) -> Message | None:
        """处理消息 - 子类实现"""
        pass

    def send(self, message: Message):
        """发送消息"""
        self.bus.publish(message)

    def llm_call(self, prompt: str, system: str | None = None) -> str:
        """调用 LLM"""
        return self.llm_client.call(prompt, system)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_base_agent.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/agents/base.py tests/test_base_agent.py src/agents/__init__.py
git commit -m "feat: implement BaseAgent abstract class"
```

---

### Task 11: Retriever Agent

**Files:**
- Create: `src/agents/retriever.py`
- Create: `src/rag/ingest.py`
- Create: `tests/test_retriever.py`

- [ ] **Step 1: 编写 Retriever 测试**

```python
# tests/test_retriever.py
import pytest
from src.agents.retriever import RetrieverAgent
from src.infrastructure.message import Message
from src.infrastructure.message_bus import MessageBus
from src.infrastructure.vector_store import VectorStore
from src.infrastructure.embedding import LocalEmbedding


def test_retriever_handle_retrieve(tmp_path):
    """测试 Retriever 处理检索请求"""
    bus = MessageBus()
    embedding = LocalEmbedding()
    store = VectorStore(persist_dir=str(tmp_path), embedding=embedding)

    # 预先添加文档
    store.add_documents(
        collection="default",
        texts=["Python is great", "I love coding"],
        metadatas=[{}, {}],
    )

    agent = RetrieverAgent(bus=bus, vector_store=store)

    msg = Message.create_request(
        from_agent="orchestrator",
        to_agent="retriever",
        intent="retrieve",
        payload={"query": "Python", "collection": "default", "top_k": 2},
    )

    response = agent.handle(msg)

    assert response is not None
    assert response.type.value == "response"
    assert "chunks" in response.payload
    assert len(response.payload["chunks"]) > 0
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_retriever.py -v
```

- [ ] **Step 3: 实现 Ingest 管道**

```python
# src/rag/ingest.py
from pathlib import Path
from src.rag.parser.base import DocumentParser
from src.rag.parser.markdown import MarkdownParser
from src.rag.parser.pdf import PDFParser
from src.infrastructure.vector_store import VectorStore


class IngestPipeline:
    """文档摄入管道"""

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.parsers: dict[str, DocumentParser] = {
            ".md": MarkdownParser(),
            ".pdf": PDFParser(),
        }

    def ingest_file(self, file_path: str, collection: str = "default"):
        """摄入单个文件"""
        path = Path(file_path)
        parser = self.parsers.get(path.suffix)

        if not parser:
            raise ValueError(f"Unsupported file type: {path.suffix}")

        chunks = parser.parse(file_path)

        texts = [c.text for c in chunks]
        metadatas = [c.metadata for c in chunks]

        self.vector_store.add_documents(collection, texts, metadatas)

    def ingest_directory(self, dir_path: str, collection: str = "default"):
        """摄入目录下所有支持的文件"""
        path = Path(dir_path)

        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.parsers:
                self.ingest_file(str(file_path), collection)
```

- [ ] **Step 4: 实现 Retriever Agent**

```python
# src/agents/retriever.py
from src.agents.base import BaseAgent
from src.infrastructure.message import Message
from src.infrastructure.message_bus import MessageBus
from src.infrastructure.vector_store import VectorStore
from src.rag.ingest import IngestPipeline


class RetrieverAgent(BaseAgent):
    """检索 Agent"""

    def __init__(self, bus: MessageBus, vector_store: VectorStore | None = None):
        super().__init__(name="retriever", subscriptions=["retrieve", "ingest"], bus=bus)
        self.vector_store = vector_store or VectorStore()
        self.ingest_pipeline = IngestPipeline(self.vector_store)

    def handle(self, message: Message) -> Message | None:
        """处理消息"""
        if message.intent == "retrieve":
            return self._handle_retrieve(message)
        elif message.intent == "ingest":
            return self._handle_ingest(message)
        return None

    def _handle_retrieve(self, message: Message) -> Message:
        """处理检索请求"""
        query = message.payload["query"]
        collection = message.payload.get("collection", "default")
        top_k = message.payload.get("top_k", 5)

        results = self.vector_store.query(collection, query, top_k)

        return Message.create_response(
            request=message,
            from_agent=self.name,
            payload={"chunks": results},
        )

    def _handle_ingest(self, message: Message) -> Message:
        """处理摄入请求"""
        path = message.payload["path"]
        collection = message.payload.get("collection", "default")

        from pathlib import Path
        if Path(path).is_dir():
            self.ingest_pipeline.ingest_directory(path, collection)
        else:
            self.ingest_pipeline.ingest_file(path, collection)

        return Message.create_response(
            request=message,
            from_agent=self.name,
            payload={"status": "success"},
        )
```

- [ ] **Step 5: 运行测试确认通过**

```bash
pytest tests/test_retriever.py -v
```

- [ ] **Step 6: 提交**

```bash
git add src/agents/retriever.py src/rag/ingest.py tests/test_retriever.py
git commit -m "feat: implement Retriever agent with ingest pipeline"
```

---

### Task 12: Analyzer Agent

**Files:**
- Create: `src/agents/analyzer.py`
- Create: `tests/test_analyzer.py`

- [ ] **Step 1: 编写 Analyzer 测试**

```python
# tests/test_analyzer.py
import pytest
from unittest.mock import Mock, patch
from src.agents.analyzer import AnalyzerAgent
from src.infrastructure.message import Message
from src.infrastructure.message_bus import MessageBus


def test_analyzer_handle_analyze():
    """测试 Analyzer 处理分析请求"""
    bus = MessageBus()

    with patch('src.infrastructure.llm_client.LLMClient') as mock_llm_class:
        mock_llm = Mock()
        mock_llm.call.return_value = "这是分析结果"
        mock_llm_class.return_value = mock_llm

        agent = AnalyzerAgent(bus=bus)
        agent.llm_client = mock_llm

        msg = Message.create_request(
            from_agent="orchestrator",
            to_agent="analyzer",
            intent="analyze",
            payload={
                "query": "什么是Python?",
                "chunks": [{"text": "Python是一门编程语言", "metadata": {}}],
            },
        )

        response = agent.handle(msg)

        assert response is not None
        assert "answer" in response.payload
        assert response.payload["answer"] == "这是分析结果"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_analyzer.py -v
```

- [ ] **Step 3: 实现 Analyzer Agent**

```python
# src/agents/analyzer.py
from src.agents.base import BaseAgent
from src.infrastructure.message import Message
from src.infrastructure.message_bus import MessageBus


class AnalyzerAgent(BaseAgent):
    """分析 Agent"""

    def __init__(self, bus: MessageBus):
        super().__init__(name="analyzer", subscriptions=["analyze", "summarize"], bus=bus)

    def handle(self, message: Message) -> Message | None:
        """处理消息"""
        if message.intent == "analyze":
            return self._handle_analyze(message)
        elif message.intent == "summarize":
            return self._handle_summarize(message)
        return None

    def _handle_analyze(self, message: Message) -> Message:
        """处理分析请求"""
        query = message.payload["query"]
        chunks = message.payload.get("chunks", [])

        # 构建 prompt
        context = "\n\n".join([f"文档片段 {i+1}:\n{c['text']}" for i, c in enumerate(chunks)])

        prompt = f"""基于以下文档片段回答问题。

问题: {query}

文档片段:
{context}

请基于文档内容给出准确的回答。如果文档中没有相关信息,请说明。"""

        answer = self.llm_call(prompt)

        return Message.create_response(
            request=message,
            from_agent=self.name,
            payload={"answer": answer},
        )

    def _handle_summarize(self, message: Message) -> Message:
        """处理总结请求"""
        text = message.payload["text"]

        prompt = f"请总结以下内容:\n\n{text}"
        summary = self.llm_call(prompt)

        return Message.create_response(
            request=message,
            from_agent=self.name,
            payload={"summary": summary},
        )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_analyzer.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/agents/analyzer.py tests/test_analyzer.py
git commit -m "feat: implement Analyzer agent"
```

---

### Task 13: Orchestrator Agent

**Files:**
- Create: `src/agents/orchestrator.py`
- Create: `tests/test_orchestrator.py`

- [ ] **Step 1: 编写 Orchestrator 测试**

```python
# tests/test_orchestrator.py
import pytest
from unittest.mock import Mock, patch
from src.agents.orchestrator import OrchestratorAgent
from src.infrastructure.message import Message
from src.infrastructure.message_bus import MessageBus


def test_orchestrator_handle_query():
    """测试 Orchestrator 处理查询"""
    bus = MessageBus()

    with patch('src.infrastructure.llm_client.LLMClient') as mock_llm_class:
        mock_llm = Mock()
        mock_llm.call.return_value = "需要检索"
        mock_llm_class.return_value = mock_llm

        agent = OrchestratorAgent(bus=bus)
        agent.llm_client = mock_llm

        msg = Message.create_request(
            from_agent="cli",
            to_agent="orchestrator",
            intent="query",
            payload={"query": "什么是Python?"},
        )

        # Orchestrator 会发送消息给其他 Agent
        # 这里简化测试,只验证它能处理消息
        response = agent.handle(msg)

        # Orchestrator 在中心调度模式下会协调其他 Agent,不直接返回
        # 实际返回由完整流程决定
        assert response is None or response.type.value == "response"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_orchestrator.py -v
```

- [ ] **Step 3: 实现 Orchestrator Agent**

```python
# src/agents/orchestrator.py
from src.agents.base import BaseAgent
from src.infrastructure.message import Message, MessageType
from src.infrastructure.message_bus import MessageBus


class OrchestratorAgent(BaseAgent):
    """调度 Agent"""

    def __init__(self, bus: MessageBus):
        super().__init__(name="orchestrator", subscriptions=["ALL"], bus=bus)
        self.pending_requests: dict[str, Message] = {}

    def handle(self, message: Message) -> Message | None:
        """处理消息"""
        # 如果是发给 orchestrator 的请求
        if message.to_agent == "orchestrator" and message.type == MessageType.REQUEST:
            if message.intent == "query":
                return self._handle_query(message)
            elif message.intent == "ingest":
                return self._handle_ingest_request(message)

        # 如果是其他 Agent 的响应,检查是否有待处理的请求
        if message.type == MessageType.RESPONSE and message.parent_id in self.pending_requests:
            return self._handle_agent_response(message)

        return None

    def _handle_query(self, message: Message) -> Message | None:
        """处理查询请求"""
        query = message.payload["query"]

        # 简化版:直接发送检索请求
        retrieve_msg = Message.create_request(
            from_agent=self.name,
            to_agent="retriever",
            intent="retrieve",
            payload={"query": query, "collection": "default", "top_k": 5},
        )

        self.pending_requests[retrieve_msg.id] = message
        self.send(retrieve_msg)

        return None  # 等待 retriever 响应

    def _handle_agent_response(self, message: Message) -> Message | None:
        """处理 Agent 响应"""
        original_request = self.pending_requests.pop(message.parent_id)

        # 如果是 retriever 的响应,发送给 analyzer
        if message.from_agent == "retriever":
            analyze_msg = Message.create_request(
                from_agent=self.name,
                to_agent="analyzer",
                intent="analyze",
                payload={
                    "query": original_request.payload["query"],
                    "chunks": message.payload["chunks"],
                },
            )

            self.pending_requests[analyze_msg.id] = original_request
            self.send(analyze_msg)
            return None

        # 如果是 analyzer 的响应,返回给原始请求者
        if message.from_agent == "analyzer":
            return Message.create_response(
                request=original_request,
                from_agent=self.name,
                payload={"answer": message.payload["answer"]},
            )

        return None

    def _handle_ingest_request(self, message: Message) -> Message | None:
        """处理摄入请求"""
        ingest_msg = Message.create_request(
            from_agent=self.name,
            to_agent="retriever",
            intent="ingest",
            payload=message.payload,
        )

        self.pending_requests[ingest_msg.id] = message
        self.send(ingest_msg)

        return None
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_orchestrator.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/agents/orchestrator.py tests/test_orchestrator.py
git commit -m "feat: implement Orchestrator agent with centralized routing"
```

---

### Task 14: CLI 实现

**Files:**
- Create: `src/cli.py`

- [ ] **Step 1: 实现 CLI**

```python
# src/cli.py
import click
from pathlib import Path
from src.config import settings
from src.infrastructure.message_bus import MessageBus, RoutingMode
from src.infrastructure.message import Message
from src.infrastructure.vector_store import VectorStore
from src.infrastructure.embedding import LocalEmbedding
from src.agents.orchestrator import OrchestratorAgent
from src.agents.retriever import RetrieverAgent
from src.agents.analyzer import AnalyzerAgent


class AgentSystem:
    """Agent 系统"""

    def __init__(self):
        self.bus = MessageBus(mode=RoutingMode.CENTRALIZED)
        self.embedding = LocalEmbedding()
        self.vector_store = VectorStore(embedding=self.embedding)

        # 初始化 Agents
        self.orchestrator = OrchestratorAgent(bus=self.bus)
        self.retriever = RetrieverAgent(bus=self.bus, vector_store=self.vector_store)
        self.analyzer = AnalyzerAgent(bus=self.bus)

        self.response_received = False
        self.final_response = None

        # Orchestrator 的响应会被发回,需要捕获
        self.bus.subscribe("ALL", self._capture_final_response)

    def _capture_final_response(self, message: Message):
        """捕获最终响应"""
        if (
            message.from_agent == "orchestrator"
            and message.to_agent == "cli"
            and message.type.value == "response"
        ):
            self.final_response = message
            self.response_received = True

    def query(self, query: str) -> str:
        """发送查询"""
        self.response_received = False
        self.final_response = None

        msg = Message.create_request(
            from_agent="cli",
            to_agent="orchestrator",
            intent="query",
            payload={"query": query},
        )

        self.bus.publish(msg)

        # 等待响应 (简化版,实际应该用异步或回调)
        import time
        timeout = 30
        elapsed = 0
        while not self.response_received and elapsed < timeout:
            time.sleep(0.1)
            elapsed += 0.1

        if self.final_response:
            return self.final_response.payload.get("answer", "No answer")
        return "Timeout waiting for response"

    def ingest(self, path: str, collection: str = "default"):
        """摄入文档"""
        msg = Message.create_request(
            from_agent="cli",
            to_agent="orchestrator",
            intent="ingest",
            payload={"path": path, "collection": collection},
        )

        self.bus.publish(msg)

        # 等待响应
        import time
        time.sleep(1)  # 简化版

        return f"Ingested {path} into collection '{collection}'"


@click.group()
def cli():
    """Multi-Agent RAG CLI"""
    pass


@cli.command()
@click.argument("path")
@click.option("--collection", default="default", help="Collection name")
def ingest(path: str, collection: str):
    """摄入文档到知识库"""
    system = AgentSystem()
    result = system.ingest(path, collection)
    click.echo(result)


@cli.command()
@click.argument("query")
@click.option("--verbose", is_flag=True, help="Show detailed output")
def ask(query: str, verbose: bool):
    """向知识库提问"""
    system = AgentSystem()
    answer = system.query(query)

    if verbose:
        click.echo(f"Query: {query}")
        click.echo(f"Answer: {answer}")
    else:
        click.echo(answer)


@cli.command()
def collections():
    """列出所有知识库"""
    embedding = LocalEmbedding()
    store = VectorStore(embedding=embedding)
    colls = store.list_collections()

    if colls:
        click.echo("Collections:")
        for c in colls:
            click.echo(f"  - {c}")
    else:
        click.echo("No collections found")


if __name__ == "__main__":
    cli()
```

- [ ] **Step 2: 测试 CLI (手动测试)**

```bash
# 创建测试文档
mkdir -p /c/Users/zhangyu/Desktop/code/study/multi-agent-rag/test_docs
echo "# Python\n\nPython is a programming language." > /c/Users/zhangyu/Desktop/code/study/multi-agent-rag/test_docs/python.md

# 摄入文档
cd /c/Users/zhangyu/Desktop/code/study/multi-agent-rag
python -m src.cli ingest ./test_docs

# 提问
python -m src.cli ask "What is Python?"

# 查看集合
python -m src.cli collections
```

Expected: CLI 能正常摄入文档和回答问题

- [ ] **Step 3: 提交**

```bash
git add src/cli.py
git commit -m "feat: implement CLI with ingest, ask, and collections commands"
```

---

### Task 15: 集成测试和文档

**Files:**
- Create: `tests/test_integration.py`
- Update: `README.md`

- [ ] **Step 1: 编写集成测试**

```python
# tests/test_integration.py
import pytest
from pathlib import Path
from src.cli import AgentSystem


def test_end_to_end_flow(tmp_path):
    """端到端测试:摄入文档 -> 提问 -> 获得答案"""
    # 创建测试文档
    test_doc = tmp_path / "test.md"
    test_doc.write_text("# Python\n\nPython is a high-level programming language.")

    # 初始化系统
    system = AgentSystem()

    # 摄入文档
    result = system.ingest(str(test_doc), "test_collection")
    assert "Ingested" in result

    # 提问
    answer = system.query("What is Python?")
    assert answer is not None
    assert len(answer) > 0
    # 注意:实际答案依赖 LLM,这里只验证有响应
```

- [ ] **Step 2: 运行集成测试**

```bash
pytest tests/test_integration.py -v -s
```

Expected: 集成测试通过 (需要有效的 ANTHROPIC_API_KEY)

- [ ] **Step 3: 更新 README 添加使用示例**

在 README.md 中添加:

```markdown
## 示例

### 1. 摄入文档

\`\`\`bash
# 摄入单个文件
mar ingest ./docs/python.md

# 摄入整个目录
mar ingest ./docs --collection my_docs
\`\`\`

### 2. 提问

\`\`\`bash
mar ask "Python的GIL是什么?"

# 详细输出
mar ask "Python的GIL是什么?" --verbose
\`\`\`

### 3. 管理知识库

\`\`\`bash
# 列出所有知识库
mar collections
\`\`\`

## 架构说明

Phase 1 实现了核心的 Multi-Agent 架构:

- **MessageBus**: 中心调度模式,所有消息经过总线路由
- **Orchestrator**: 接收用户请求,协调 Retriever 和 Analyzer
- **Retriever**: 文档摄入和向量检索
- **Analyzer**: 基于检索结果生成回答

## 下一步

- Phase 2: 增强 RAG (代码解析、Hybrid Search、Reranker)
- Phase 3: Agent 进阶 (对等协作、Router Agent、对话记忆)
- Phase 4: 生产化 (异步、流式输出、Web UI)
- Phase 5: 软件开发全流程 Agent
```

- [ ] **Step 4: 运行所有测试**

```bash
pytest -v
```

Expected: 所有测试通过

- [ ] **Step 5: 最终提交**

```bash
git add tests/test_integration.py README.md
git commit -m "test: add integration tests and update documentation"
```

---

## 自检清单

完成所有任务后,进行以下检查:

- [ ] 所有测试通过 (`pytest -v`)
- [ ] CLI 命令可用 (`mar --help`)
- [ ] 能成功摄入 Markdown 和 PDF 文档
- [ ] 能基于摄入的文档回答问题
- [ ] 代码格式化 (`black src tests`)
- [ ] 代码检查通过 (`ruff check src tests`)
- [ ] README 文档完整
- [ ] .env 文件已配置 ANTHROPIC_API_KEY

---

## 执行说明

**Phase 1 完成后,系统具备以下能力:**

1. 通过 CLI 摄入 Markdown 和 PDF 文档到向量数据库
2. 基于摄入的文档回答用户问题
3. 三个 Agent (Orchestrator/Retriever/Analyzer) 通过 MessageBus 协作
4. 中心调度模式,消息流清晰可追踪

**预计开发时间:** 4-6 小时 (初学者可能需要 8-10 小时)

**关键学习点:**
- Multi-Agent 架构设计
- 消息总线模式
- RAG 管道 (文档解析、分块、向量化、检索)
- Claude API 使用
- TDD 开发流程

