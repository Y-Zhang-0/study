"""fetcher 命令行入口(D6:Click + asyncio)。

把 client.py 的异步抓取能力,包装成可在终端调用的命令行工具。
对照 Node 的 commander.js:Click 用装饰器声明式定义命令 / 选项 / 参数。

填写指引(主公亲手写,臣只搭骨架):
  1. import:click、asyncio,以及 client 里要用的 fetch_posts(按需再加 Post)。
  2. 用 @click.group() 定义命令组 cli()  —— 它是"总机",负责派发子命令。
  3. 子命令一:fetch
       @cli.command()
       @click.argument("ids", nargs=-1, type=int)   # 变长位置参数,拿到 tuple
       命令体内:asyncio.run(fetch_posts(list(ids)))  # 同步壳里启动一次事件循环
       再把结果用 click.echo 友好输出(数量 / 标题 / 失败提示)。
  4. 子命令二:自拟(如 report 统计字数、batch 按文件批量、count 仅计数 ...)。
       要求与 fetch 是不同职责,凑满"≥2 子命令"。
  5. 健壮性:单个失败不崩(client 已用 gather(return_exceptions=True));
       命令级错误用 raise click.ClickException("...") 给非 0 退出码。
  6. 不要写 if __name__ == "__main__"——入口走 pyproject 的 [project.scripts]。

配套(主公自己改 pyproject.toml):
  - dependencies 加 "click>=8.1"
  - 新增 [project.scripts]:  fetcher = "fetcher.cli:cli"
  - 改完重装:uv pip install -e .
"""

# TODO(主公): 按上方指引实现 cli 命令组与两个子命令。
import click
import asyncio
from fetcher.client import fetch_posts, batch_iter, Post


@click.group()
def cli():
    pass


@click.command()
def hello():
    click.echo("hello world")


@cli.command()
@click.argument("ids", nargs=-1, type=int)
def fetch(ids: tuple[int, ...]) -> None:
    if not ids:
        raise click.ClickException("请至少提供一个 post id")
    # asyncio.run 会返回协程的返回值
    posts = asyncio.run(fetch_posts(list(ids)))
    for post in posts:
        click.echo(f"ID: {post.id} | Title: {post.title}")
    click.echo(f"Fetched {len(posts)} posts")


# @cli.command() 就是 @click.command() + cli.add_command() 的合体语法糖。
# 一步干两件事:① 把函数变成 Command 对象;② 立刻挂到 cli 这个 group 下。
cli.add_command(hello)


async def fetch_in_batch(ids: list[int], batch_size: int) -> list[Post]:
    posts: list[Post] = []
    # 同步 with 包住含 await 的循环:progressbar 进出门不需 await,故普通 with(非 async with)
    with click.progressbar(length=len(ids), label="抓取中") as bar:
        for batch in batch_iter(ids, batch_size):
            posts.extend(await fetch_posts(batch))
            bar.update(len(batch))
    return posts


@cli.command()
@click.option("--start", type=int, required=True, help="开始 post id")
@click.option("--end", type=int, required=True, help="结束 post id")
@click.option("--batch-size", default=5, type=click.IntRange(1, 50), help="批量大小(1-50)")
def batch(start: int, end: int, batch_size: int) -> None:
    click.secho(f"batch posts {start} to {end} with batch size {batch_size} posts", fg="green")
    ids = list(range(start, end + 1))
    if not ids:
        raise click.ClickException("start must be less than end")
    posts = asyncio.run(fetch_in_batch(ids, batch_size))
    for post in posts:
        click.secho(f"ID: {post.id} | Title: {post.title}", fg="green")
    click.secho(f"Fetched {len(posts)} posts", fg="green")
