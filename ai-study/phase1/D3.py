from contextlib import contextmanager
import time
import functools
from pydantic import BaseModel, Field
import httpx
import asyncio
def batch_iter(items: list, batch_size: int):
    result = []
    count = 0
    for item in items:
        result.append(item)
        count += 1
        if count == batch_size:
            yield result
            result = []
            count = 0
    if result:
        yield result

gen = batch_iter([1,2,3,4,5,6,7], 3)
print(f"1: {list(gen)}")
print(f"2: {list(gen)}")
# 输出: 空白 因为生成器对象在第一次遍历结束后就消耗殆尽了 迭代到了StopIteration 所以第二次不会再产生任何值。
# 简洁写法
def batch_iter_simple(items: list, batch_size: int):
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

@contextmanager
def timer(label: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print(f"{label} took {end - start:.3f} seconds")

with timer("batch_iter"):
    try:
        list(batch_iter([1,2,3,4,5,6,7], 3))
        1 / 0
    except ZeroDivisionError as e:
        print(f"error {e}")     
    finally:
        pass


def async_time(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper

class Post(BaseModel):
    user_id: int = Field(..., gt=0, alias="userId")
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1, max_length=1000)

async def fetch(client: httpx.AsyncClient, path: str) -> dict:
    resp = await client.get(path)
    resp.raise_for_status()
    return resp.json()

@async_time
async def fetch_posts(post_ids: list[int]) -> list[Post]:
    posts = []
    timeout = httpx.Timeout(15, connect=5)
    async with httpx.AsyncClient(
            base_url="https://jsonplaceholder.typicode.com",
            timeout=timeout
        ) as client:
        responses = await asyncio.gather(*(fetch(client, f"/posts/{post_id}") for post_id in post_ids),
        return_exceptions=True)
        for post_id, response in zip(post_ids, responses):
            if isinstance(response, Exception):
                print(f"Error: post {post_id} failed, {type(response).__name__}: {response}")
                continue
            post = Post(**response)
            posts.append(post)
        return posts

asyncio.run(fetch_posts([1,2,3,4,5,6,7,8,9,10,99999]))