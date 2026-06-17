# fetcher

`fetcher` 是 Phase 1 的 Python 工程化练习项目，用来串起 `httpx`、`asyncio`、Pydantic、Click、pytest 与 `src` 布局。

它目前不是作品集级产品，而是一个可安装、可运行、可测试的小型 CLI 工程样板。

## 功能

- 按 post id 抓取 JSONPlaceholder 的 posts。
- 支持单个失败隔离，失败项不会拖垮整批结果。
- 支持基础重试与指数退避。
- 支持 `asyncio.Semaphore` 控制批量抓取并发上限。
- 提供 Click CLI：`fetch`、`batch`、`hello`。
- 提供离线测试：单元测试 + Click `CliRunner` 集成测试。

## 安装

在本目录下创建虚拟环境并安装开发依赖：

```powershell
uv venv
.\.venv\Scripts\activate
uv pip install -e ".[dev]"
```

如果不用 `uv`，也可以使用当前虚拟环境里的 `python -m pip install -e ".[dev]"`。

## 使用

安装后可以直接使用命令行入口：

```powershell
fetcher fetch 1 2 3
```

批量抓取：

```powershell
fetcher batch --start 1 --end 10 --batch-size 5
```

说明：

- `fetch` 至少需要一个 post id。
- `batch` 中 `batch-size` 范围是 `1..50`。
- `batch` 的 `start` 大于 `end` 时会返回 Click 业务错误。

## 开发验证

运行测试与覆盖率：

```powershell
.\.venv\Scripts\python.exe -m pytest --cov=fetcher --cov-report=term-missing
```

运行 lint：

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests
```

当前 D7 收口状态：

- 测试：`22 passed`
- 覆盖率：`90%`
- Ruff：clean

## 项目结构

```text
phase1/fetcher/
├── pyproject.toml
├── src/
│   └── fetcher/
│       ├── __init__.py
│       ├── cli.py
│       └── client.py
└── tests/
    ├── test_cli.py
    └── test_client.py
```

## 关键设计

### `src` 布局

项目代码放在 `src/fetcher` 下，测试需要通过可编辑安装后的包导入代码。这样可以避免“测试误用当前目录源码导致假绿”的问题。

### `fetch_posts`

`fetch_posts` 负责：

- 创建 `httpx.AsyncClient`。
- 用 `asyncio.Semaphore` 限制并发。
- 用 `asyncio.gather(..., return_exceptions=True)` 做失败隔离。
- 把成功响应转换成 Pydantic `Post` 模型。

### CLI

`cli.py` 负责把异步抓取能力包装成同步命令行入口。Click 命令函数内部用 `asyncio.run(...)` 启动协程。

## 已知限制

- 当前抓取目标固定为 JSONPlaceholder。
- 重试策略仍是基础版，尚未区分 `429`、`5xx`、`4xx`。
- 退避策略尚未加入 jitter。
- CLI 输出仍偏练习性质，没有面向真实业务场景设计。
- 项目还没有配置化、日志、真实数据源或可视化展示。

## 后续改进

- 增加配置化 base URL、超时、并发数和重试策略。
- 精细化重试：超时、`429`、`5xx` 可重试，普通 `4xx` 不重试。
- 为指数退避加入 jitter，降低同步重试导致的流量尖峰。
- 增加结构化日志。
- 设计一个更贴近真实业务的落地场景，例如批量采集接口健康状态或生成轻量报告。
