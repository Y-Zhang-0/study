# Multi-Agent RAG System

AI 驱动的 Multi-Agent 协作系统,支持文档问答和软件开发全流程。

## 快速开始

### 1. 安装依赖

```bash
pip install -e ".[dev]"
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件,填入你的 ANTHROPIC_API_KEY
```

### 3. 使用 CLI

```bash
# 摄入文档
mar ingest ./docs

# 问答
mar ask "Python的GIL是什么?"

# 查看知识库
mar collections
```

## 使用示例

### 文档摄入

```python
from pathlib import Path
from src.rag.ingest import IngestPipeline
from src.rag.parser.markdown import MarkdownParser
from src.rag.chunker import SemanticChunker
from src.infrastructure.embedding import OpenAIEmbedding
from src.infrastructure.vector_store import InMemoryVectorStore

# 初始化组件
parser = MarkdownParser()
chunker = SemanticChunker(chunk_size=512, overlap=50)
embedding = OpenAIEmbedding(api_key="your-key")
vector_store = InMemoryVectorStore()

# 创建摄入管道
pipeline = IngestPipeline(parser, chunker, embedding, vector_store)

# 摄入单个文档
await pipeline.ingest_document(Path("./docs/python.md"))

# 摄入整个目录
result = await pipeline.ingest_directory(Path("./docs"))
print(f"Processed {result['processed']} files")
```

### Agent 协作查询

```python
from src.agents.orchestrator import OrchestratorAgent
from src.agents.retriever import RetrieverAgent
from src.agents.analyzer import AnalyzerAgent
from src.infrastructure.message import Message
from src.infrastructure.llm_client import AnthropicClient

# 初始化 LLM 客户端
llm_client = AnthropicClient(api_key="your-key")

# 创建 Agent
retriever = RetrieverAgent(
    agent_id="retriever",
    config={"vector_store": vector_store, "embedding": embedding}
)

analyzer = AnalyzerAgent(
    agent_id="analyzer",
    config={"llm_client": llm_client}
)

orchestrator = OrchestratorAgent(
    agent_id="orchestrator",
    config={"retriever": retriever, "analyzer": analyzer}
)

# 发送查询
query_msg = Message.create_request(
    from_agent="user",
    to_agent="orchestrator",
    intent="query",
    payload={"query": "What is Python GIL?"}
)

response = await orchestrator.process(query_msg)
print(response.payload["answer"])
```

### MessageBus 事件驱动

```python
from src.infrastructure.message_bus import MessageBus
from src.infrastructure.message import Message

bus = MessageBus()

# 订阅事件
async def handle_query(msg: Message):
    print(f"Received query: {msg.payload['query']}")

bus.subscribe("query", handle_query)

# 发布事件
await bus.publish(Message.create_request(
    from_agent="user",
    to_agent="system",
    intent="query",
    payload={"query": "test"}
))
```

## 架构

- **Infrastructure 层**: MessageBus, LLM Client, VectorStore, Embedding
- **Agent 层**: Orchestrator, Retriever, Analyzer
- **Application 层**: CLI

## 开发

```bash
# 运行测试
pytest

# 运行集成测试
pytest tests/test_integration.py

# 代码格式化
black src tests
ruff check src tests
```
