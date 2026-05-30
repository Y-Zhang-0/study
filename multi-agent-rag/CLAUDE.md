# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Multi-Agent RAG 系统 — 基于消息驱动的多智能体协作框架，支持文档摄入、向量检索与智能问答。

核心技术栈：Anthropic Claude API + ChromaDB + sentence-transformers + Click CLI

## 常用命令

```bash
# 安装依赖（开发模式）
pip install -e ".[dev]"

# 运行全部测试
pytest

# 运行单个测试文件
pytest tests/test_integration.py -v

# 运行单个测试类
pytest tests/test_base_agent.py::TestBaseAgent -v

# 运行单个测试用例
pytest tests/test_chunker.py::TestChunker::test_chunk_text -v

# 代码格式化
black src tests

# 代码检查
ruff check src tests

# CLI 使用
mar ingest ./docs                    # 摄入文档目录
mar ingest ./docs/file.pdf           # 摄入单个文件
mar ask "Python GIL 是什么?"         # 问答
mar collections list                 # 列出所有集合
mar collections delete <name>        # 删除集合
```

## 架构设计

### 三层架构

```
Infrastructure 层（基础设施）
├── Message/MessageBus    # 消息协议与事件总线
├── LLMClient            # Anthropic Claude API 封装
├── EmbeddingProvider    # sentence-transformers 封装
└── VectorStore          # ChromaDB 封装

Agent 层（智能体）
├── BaseAgent            # 抽象基类，定义 process(Message) -> Message 接口
├── RetrieverAgent       # 向量检索智能体
├── AnalyzerAgent        # LLM 分析智能体
└── OrchestratorAgent    # 编排智能体（协调 Retriever + Analyzer）

Application 层（应用）
├── IngestPipeline       # 文档摄入管道（Parser → Chunker → Embedding → VectorStore）
└── CLI                  # Click 命令行接口
```

### 消息协议

所有 Agent 通信遵循统一消息协议（`src/infrastructure/message.py`）：

- **Message 字段**：`id`, `from_agent`, `to_agent`, `type`（REQUEST/RESPONSE/EVENT）, `intent`, `payload`, `context`, `parent_id`
- **创建方式**：
  - `Message.create_request()` — 创建请求消息
  - `Message.create_response(request, ...)` — 基于请求创建响应（自动关联 parent_id）

### Agent 实现规范

所有 Agent 继承 `BaseAgent`，必须实现 `async def process(message: Message) -> Message`：

1. 检查 `message.intent` 判断处理逻辑
2. 从 `message.payload` 提取输入参数
3. 执行业务逻辑
4. 返回 `Message.create_response(message, from_agent=self.agent_id, payload={...})`

### 配置管理

配置通过 `src/config.py` 的 `Settings` 类管理（pydantic-settings），从环境变量或 `.env` 文件加载：

- `ANTHROPIC_API_KEY` — Claude API 密钥（必需）
- `EMBEDDING_MODEL` — 嵌入模型（默认 `sentence-transformers/all-MiniLM-L6-v2`）
- `CHROMA_PERSIST_DIR` — ChromaDB 持久化目录（默认 `./chroma_db`）
- `CHUNK_SIZE` / `CHUNK_OVERLAP` — 文本分块参数
- `LLM_MODEL` / `LLM_MAX_TOKENS` / `LLM_TEMPERATURE` — LLM 参数

使用 `get_settings()` 获取单例配置对象。

## 关键设计点

1. **消息驱动架构**：Agent 间通过 Message 通信，MessageBus 支持发布/订阅模式
2. **异步优先**：所有 Agent 的 `process()` 方法均为 async，CLI 使用 `asyncio.run()`
3. **依赖注入**：Agent 通过构造函数的 `config` 字典接收依赖（embedding, vector_store, llm 等）
4. **Parser 扩展**：新增文档格式需实现 `BaseParser` 接口（`parse(file_path) -> List[Document]`）
5. **测试隔离**：测试使用内存向量库，无需真实 ChromaDB 或 API 密钥

## 开发注意事项

- 新增 Agent 时必须继承 `BaseAgent` 并实现 `process()` 方法
- 修改消息协议需同步更新所有 Agent 的消息处理逻辑
- CLI 命令需在 `src/cli.py` 中注册，入口点为 `pyproject.toml` 的 `[project.scripts]`
- 向量库持久化目录默认为 `./chroma_db`，测试时使用临时目录
