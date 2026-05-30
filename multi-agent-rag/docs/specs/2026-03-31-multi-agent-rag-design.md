# Multi-Agent RAG 系统设计文档

> 日期: 2026-03-31
> 状态: 已确认
> 技术栈: Python / Claude API / ChromaDB

## 1. 项目概述

一个集成 RAG 能力的 Multi-Agent 协作系统，用于通用文档问答。通过分层混合架构，支持从中心调度到对等协作的渐进演进。CLI 交互，专注后端架构学习。

项目路径：`C:\Users\zhangyu\Desktop\code\study\multi-agent-rag\`

## 2. 整体架构

三层架构：

```
┌─────────────────────────────────────────┐
│           Application Layer             │
│  CLI 交互 → Orchestrator → 结果输出       │
├─────────────────────────────────────────┤
│            Agent Layer                  │
│  Orchestrator / Retriever / Analyzer    │
│  (通过 MessageBus 通信)                  │
├─────────────────────────────────────────┤
│          Infrastructure Layer           │
│  MessageBus / LLM Client / VectorStore  │
│  DocumentParser / EmbeddingProvider     │
└─────────────────────────────────────────┘
```

关键设计决策：

- **MessageBus 是核心**：所有 Agent 通信都经过 MessageBus，不直接互调。Orchestrator 只是一个"默认订阅所有消息"的特殊 Agent，不是硬编码的中心。未来任何 Agent 都可以订阅其他 Agent 的消息，自然过渡到对等模式。
- **Agent 统一接口**：每个 Agent 实现相同的 BaseAgent 接口，角色不同但协议一致。
- **Infrastructure 可插拔**：LLM、Embedding、VectorStore 都通过抽象接口隔离，方便切换实现。

## 3. Agent 通信机制

### 3.1 消息协议

```
Message {
  id:          唯一标识
  from_agent:  发送者
  to_agent:    接收者（可为 "broadcast" 广播）
  type:        REQUEST / RESPONSE / EVENT
  intent:      意图标识（如 "retrieve", "analyze", "route"）
  payload:     业务数据
  context:     对话上下文（共享状态）
  parent_id:   关联的请求消息 ID（用于追踪链路）
}
```

### 3.2 MessageBus

```
                    MessageBus
                 ┌──────────────┐
                 │  消息队列      │
                 │  路由表        │
                 │  消息历史      │
                 └──────┬───────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
    ┌─────▼─────┐ ┌────▼──────┐ ┌───▼───────┐
    │Orchestrator│ │ Retriever │ │ Analyzer  │
    │            │ │           │ │           │
    │ 订阅:      │ │ 订阅:     │ │ 订阅:      │
    │ - ALL      │ │ - retrieve│ │ - analyze │
    │            │ │ - ingest  │ │ - summarize│
    └────────────┘ └───────────┘ └───────────┘
```

路由控制：
- `mode="centralized"`：所有消息强制经过 Orchestrator
- `mode="hybrid"`：Agent 可以直接通信，Orchestrator 仍能监听所有消息做日志和兜底

### 3.3 基础模式通信流（中心调度）

```
User: "Python的GIL是什么？"

1. CLI → MessageBus → Orchestrator
   Message(type=REQUEST, intent="query", payload="Python的GIL是什么？")

2. Orchestrator → MessageBus → Retriever
   Message(type=REQUEST, intent="retrieve", payload={query: "Python GIL", top_k: 5})

3. Retriever → MessageBus → Orchestrator
   Message(type=RESPONSE, intent="retrieve", payload={chunks: [...]})

4. Orchestrator → MessageBus → Analyzer
   Message(type=REQUEST, intent="analyze", payload={query: "...", chunks: [...]})

5. Analyzer → MessageBus → Orchestrator
   Message(type=RESPONSE, intent="analyze", payload={answer: "GIL是..."})

6. Orchestrator → CLI → User
```

### 3.4 进阶模式通信流（对等协作）

```
User: "对比Python和Go的并发模型"

1. CLI → MessageBus → Orchestrator
   Message(type=REQUEST, intent="query", ...)

2. Orchestrator → MessageBus → Retriever
   Message(type=REQUEST, intent="retrieve", payload={query: "Python并发"})

3. Retriever 检索后发现结果不够，直接发消息：
   Retriever → MessageBus → Analyzer
   Message(type=REQUEST, intent="suggest_queries", payload={current: "Python并发", gap: "缺少Go相关内容"})

4. Analyzer → MessageBus → Retriever
   Message(type=RESPONSE, intent="suggest_queries", payload={queries: ["Go goroutine", "Go并发模型"]})

5. Retriever 补充检索后，汇总返回：
   Retriever → MessageBus → Orchestrator
   Message(type=RESPONSE, intent="retrieve", payload={chunks: [Python相关, Go相关]})

6. Orchestrator → Analyzer → Orchestrator → CLI → User
```

关键区别：基础模式下所有消息都经过 Orchestrator 中转；进阶模式下 Retriever 和 Analyzer 之间可以直接对话，Orchestrator 只需要等最终结果。

## 4. RAG 管道

### 4.1 文档摄入流程

```
文档文件
  │
  ▼
DocumentParser（根据文件类型分发）
  ├── MarkdownParser  → 按标题层级切分
  ├── PDFParser       → 按页/段落切分（PyMuPDF）
  └── CodeParser      → 按函数/类切分（tree-sitter）
  │
  ▼
Chunker（统一分块策略）
  ├── 块大小: 512 tokens（可配置）
  ├── 重叠: 64 tokens
  └── 保留元数据: 文件名、标题路径、语言、行号
  │
  ▼
EmbeddingProvider
  ├── LocalEmbedding  → sentence-transformers (默认)
  └── APIEmbedding    → OpenAI / Voyage（可切换）
  │
  ▼
ChromaDB（持久化存储）
  ├── collection: 按知识库名隔离
  └── metadata: 文件来源、块位置、文档类型
```

### 4.2 检索问答流程

```
用户 query
  │
  ▼
Query Embedding → 向量相似度搜索（top_k=5）
  │
  ▼
基础模式: 直接返回 chunks
  │
进阶模式: Reranker 重排序
  ├── 基于 LLM 的相关性打分
  └── 过滤低分 chunks，返回 top_n
```

### 4.3 文档解析策略

| 文档类型 | 解析库 | 切分粒度 | 元数据 |
|---------|--------|---------|--------|
| Markdown | 内置解析 | 按 `##` 标题层级 | 标题路径、文件名 |
| PDF | PyMuPDF | 按段落，跨页合并 | 页码、文件名 |
| Code | tree-sitter | 按函数/类定义 | 语言、符号名、行号 |

进阶扩展点：
- **Hybrid Search**：向量检索 + BM25 关键词检索融合，提升召回率
- **Reranker**：用 LLM 对检索结果二次排序，提升精度
- **Multi-query**：Analyzer 生成多个变体 query 并行检索合并

## 5. Agent 详细设计

### 5.1 BaseAgent 统一接口

```
BaseAgent
  ├── name: str              # Agent 标识
  ├── subscriptions: list    # 订阅的 intent 列表
  ├── handle(message) → Message    # 处理消息（核心方法）
  ├── send(message)                # 通过 MessageBus 发消息
  └── llm_call(prompt, context)    # 调用 Claude API
```

### 5.2 核心 Agent

| Agent | 职责 | 订阅 intent | 依赖 |
|-------|------|------------|------|
| Orchestrator | 接收用户问题，拆解意图，调度其他 Agent，汇总回答 | ALL | LLM Client |
| Retriever | 文档摄入、向量检索、返回相关文档片段 | retrieve, ingest | VectorStore, EmbeddingProvider, DocumentParser |
| Analyzer | 基于检索结果做推理、总结、对比分析，生成最终回答 | analyze, summarize | LLM Client |

### 5.3 Orchestrator 调度逻辑

```
收到用户 query
  │
  ▼
意图识别（LLM 判断）
  ├── 需要检索 → 发 retrieve 给 Retriever → 拿到 chunks → 发 analyze 给 Analyzer
  ├── 纯闲聊   → 直接 LLM 回答
  └── 文档摄入 → 发 ingest 给 Retriever
  │
  ▼
汇总结果，返回用户
```

## 6. 进阶路线

### Phase 1：基础版（核心功能）
- 中心调度模式，MessageBus 路由 mode="centralized"
- 三个核心 Agent 跑通完整问答链路
- RAG：Markdown + PDF 解析，本地 Embedding，ChromaDB 存储
- CLI 交互：`ingest <path>` 摄入文档，`ask <question>` 提问

### Phase 2：RAG 增强
- 新增 CodeParser（tree-sitter），支持代码库摄入
- Hybrid Search：向量检索 + BM25 关键词检索融合
- Reranker：LLM 对检索结果二次排序
- Multi-query：Analyzer 生成变体 query，Retriever 并行检索合并
- Embedding 切换到云端 API，对比效果差异

### Phase 3：Agent 进阶
- MessageBus 切换到 mode="hybrid"，开放 Agent 对等通信
- 新增 Router Agent：替代 Orchestrator 的硬编码路由，用 LLM 做智能路由决策
- Agent 自主协作：Retriever 发现信息不足时主动请求 Analyzer 建议补充查询
- 对话记忆：引入 ConversationMemory，支持多轮上下文
- Agent 可观测性：消息链路追踪、耗时统计、调用关系可视化

### Phase 4：生产化（可选）
- 异步消息处理（asyncio）
- 流式输出（streaming response）
- 错误重试与降级策略
- Web UI（Streamlit/Gradio）

### Phase 5：软件开发全流程 Agent

系统定位从「通用文档问答」升级为「AI 驱动的软件开发全流程助手」。RAG 从系统核心变为共享基础设施，所有新 Agent 都可调用检索能力。

#### 新增 Agent

| Agent | 职责 | 订阅 intent | 依赖 |
|-------|------|------------|------|
| RequirementsAgent | 需求分析、拆解用户故事、生成需求文档 | requirements | LLM + Retriever（检索类似需求） |
| DesignAgent | 方案设计、架构建议、技术选型 | design | LLM + Retriever（检索技术文档） |
| DeveloperAgent | 代码生成、代码修改建议 | develop | LLM + Retriever（检索代码库） |
| TesterAgent | 生成测试用例、执行自测、报告缺陷 | test | LLM + Retriever（检索测试规范） |

#### 全流程协作流

```
用户需求描述
  │
  ▼
Orchestrator（意图识别：开发任务）
  │
  ▼
RequirementsAgent
  ├── 检索已有需求文档（通过 Retriever）
  ├── 分析用户需求，拆解为用户故事
  └── 输出：结构化需求文档
  │
  ▼
DesignAgent
  ├── 检索相关技术文档和架构模式（通过 Retriever）
  ├── 基于需求生成技术方案
  └── 输出：设计方案文档
  │
  ▼
DeveloperAgent
  ├── 检索代码库中的相关实现（通过 Retriever）
  ├── 基于设计方案生成代码
  └── 输出：代码文件 / 修改建议
  │
  ▼
TesterAgent
  ├── 检索测试规范和已有用例（通过 Retriever）
  ├── 基于需求和代码生成测试用例
  ├── 执行测试，报告结果
  └── 输出：测试报告（通过/失败/缺陷）
  │
  ▼
Orchestrator 汇总 → 用户
```

#### 对等协作场景

- TesterAgent 发现缺陷 → 直接通知 DeveloperAgent 修复 → 修复后重新测试
- DesignAgent 发现需求不明确 → 直接请求 RequirementsAgent 补充细节
- DeveloperAgent 发现设计方案有技术障碍 → 直接反馈 DesignAgent 调整

#### CLI 扩展

```bash
# 全流程开发
mar dev "实现用户登录功能"              # 触发完整流程
mar dev --phase requirements "..."    # 只执行需求分析阶段
mar dev --phase design "..."          # 只执行方案设计阶段

# 单步操作
mar requirements "用户需要一个搜索功能"  # 仅需求分析
mar design "基于Redis实现缓存层"        # 仅方案设计
mar test ./src/auth.py                 # 仅生成测试用例
```

## 7. 项目结构

```
multi-agent-rag/
├── src/
│   ├── agents/
│   │   ├── base.py            # BaseAgent 抽象类
│   │   ├── orchestrator.py    # 调度 Agent
│   │   ├── retriever.py       # 检索 Agent
│   │   ├── analyzer.py        # 分析 Agent
│   │   ├── requirements.py    # 需求分析 Agent（Phase 5）
│   │   ├── designer.py        # 方案设计 Agent（Phase 5）
│   │   ├── developer.py       # 功能开发 Agent（Phase 5）
│   │   └── tester.py          # 自测 Agent（Phase 5）
│   ├── infrastructure/
│   │   ├── message_bus.py     # 消息总线
│   │   ├── message.py         # 消息协议定义
│   │   ├── llm_client.py      # Claude API 封装
│   │   ├── vector_store.py    # ChromaDB 封装
│   │   └── embedding.py       # Embedding 抽象层（本地/云端）
│   ├── rag/
│   │   ├── parser/
│   │   │   ├── base.py        # 解析器接口
│   │   │   ├── markdown.py    # Markdown 解析
│   │   │   ├── pdf.py         # PDF 解析
│   │   │   └── code.py        # 代码解析（Phase 2）
│   │   ├── chunker.py         # 分块策略
│   │   └── ingest.py          # 摄入管道编排
│   ├── cli.py                 # CLI 入口
│   └── config.py              # 配置管理
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

## 8. 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| LLM | Claude API (anthropic SDK) | 主力模型 |
| Embedding（本地） | sentence-transformers | 默认，免费无限调用 |
| Embedding（云端） | OpenAI / Voyage | Phase 2 切换对比 |
| 向量数据库 | ChromaDB | 轻量，纯 Python |
| PDF 解析 | PyMuPDF (fitz) | 速度快，质量好 |
| 代码解析 | tree-sitter | Phase 2，按 AST 切分 |
| CLI 框架 | click | 轻量成熟 |
| 配置管理 | pydantic-settings | 类型安全，支持 .env |
| 测试 | pytest | 标准选择 |
| 异步 | asyncio | Phase 4 引入 |

## 9. CLI 命令设计

```bash
# 文档摄入
mar ingest ./docs              # 摄入目录下所有支持的文档
mar ingest ./main.py           # 摄入单个文件
mar ingest --collection mylib  # 指定知识库名

# 问答
mar ask "Python的GIL是什么？"
mar ask --verbose "..."        # 显示检索到的文档片段和调度过程

# 知识库管理
mar collections                # 列出所有知识库
mar collections delete mylib   # 删除知识库
```
