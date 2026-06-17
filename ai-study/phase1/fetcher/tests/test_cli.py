"""D7 集成测试:用 Click 的 CliRunner 测命令行入口(fetch / batch)。

为什么需要它:
    test_client.py 测的是"函数"(fetch_posts/batch_iter…),
    但用户实际敲的是"命令"(`fetcher fetch 1 2 3`)。命令层有自己的逻辑——
    参数解析、退出码、错误提示、输出格式——只有从"命令入口"测才覆盖得到。

CliRunner 是什么(对照):
    它在【本进程内】调用你的 Click 命令,不起子进程、不打真网络,捕获 stdout 与退出码。
    类比:测 Node 的 commander 时不会真 spawn 一个进程,而是直接调命令函数断言输出。

核心三件套:
    runner = CliRunner()
    result = runner.invoke(cli, ["fetch", "1", "2"])   # 像命令行那样传 argv 列表
    result.exit_code   # 0 成功 / 2 参数用法错(UsageError) / 非0 业务失败(ClickException=1)
    result.output      # 捕获到的 stdout 文本
    result.exception   # 命令内部抛出的异常对象(调试用)

⚠️ patch 位置的坑(D4「patch 被使用的地方」活例):
    cli.py 顶部写了  `from fetcher.client import fetch_posts`
    → 名字 fetch_posts 此刻已被绑进 fetcher.cli 命名空间。
    所以要拦它,patch 的是 "fetcher.cli.fetch_posts",【不是】 "fetcher.client.fetch_posts"。
    (为什么?深挖环节展开;先记结论:patch 它被【使用】的地方。)

⚠️ 这些测试是【同步】函数:invoke 同步调用、命令体内部自跑 asyncio.run,
    所以本文件【不要】加 @pytest.mark.asyncio。

填写指引(主公亲手写,臣只给样例 + 桩):
    - test_fetch_no_args     ✅ 已给完整样例 ↓ 照此风格写其余
    - test_fetch_success     patch fetcher.cli.fetch_posts 返回 [假Post],断言 output 含标题、exit_code==0
    - test_batch_bad_range   --batch-size 越界(IntRange 1-50)→ exit_code==2
    - 自行再补:batch 正常、业务失败、空范围 等,凑足覆盖
"""

import pytest
from click.testing import CliRunner
from unittest.mock import AsyncMock

from fetcher.cli import cli
from fetcher.client import Post  # noqa: F401  造假 Post 时会用到


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# ============ 完整样例(照此写其余;本例可直接跑绿)============
def test_fetch_no_args(runner):
    """fetch 不给任何 id → 命中 ClickException → 非 0 退出 + 错误提示。"""
    result = runner.invoke(cli, ["fetch"])
    assert result.exit_code != 0
    assert "至少提供一个 post id" in result.output


# ============ 以下为桩,主公填实现(填完把 NotImplementedError 删掉)============
def test_fetch_success(runner, mocker):
    """patch fetcher.cli.fetch_posts → 返回 [一个假 Post],
    断言 output 里能看到标题、exit_code == 0、fetch_posts 被调用一次。

    提示:fetch_posts 是 async,命令体内 asyncio.run 会 await 它。
         普通 Mock 返回非协程会让 asyncio.run 崩 —— 想想用什么 mock。
    """
    fake_post = Post(userId=1, id=1, title="mock title", body="mock body")
    
    fake_fetch_posts = mocker.patch(
        "fetcher.cli.fetch_posts",
        new_callable = AsyncMock,
    )
    fake_fetch_posts.return_value = [fake_post]

    result = runner.invoke(cli, ["fetch", "1"])

    assert result.exit_code == 0
    assert "mock title" in result.output
    fake_fetch_posts.assert_awaited_once_with([1])


def test_batch_bad_range(runner):
    """batch --batch-size 越界(IntRange(1,50),传个 0 或 999)→ exit_code == 2。
    这一条不需要 patch:参数校验在进网络之前就拦下了。
    """
    result = runner.invoke(
        cli,
        ["batch", "--start", "1", "--end", "3", "--batch-size", "0"],
    )

    assert result.exit_code == 2
    assert "--batch-size" in result.output


# TODO(主公): 继续补 —— batch 正常路径、业务失败路径、空范围(start>end)等
def test_batch_success(runner, mocker):
    fake_post = Post(userId=1, id=1, title="mock title", body="mock body")

    fake_fetch_in_batch_posts = mocker.patch(
        "fetcher.cli.fetch_in_batch",
        new_callable=AsyncMock,
    )

    fake_fetch_in_batch_posts.return_value = [fake_post]

    result = runner.invoke(cli, ["batch", "--start", "1", "--end", "2", "--batch-size", "1"])

    assert result.exit_code == 0
    assert "mock title" in result.output
    fake_fetch_in_batch_posts.assert_awaited_once_with([1, 2], 1)


def test_batch_empty_range(runner):
    result = runner.invoke(cli, ["batch", "--start", "3", "--end", "1", "--batch-size", "1"])

    assert result.exit_code != 0
    assert "start must be less than end" in result.output
