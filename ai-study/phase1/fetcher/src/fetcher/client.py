from pydantic import BaseModel, Field
import httpx
import asyncio


def batch_iter(items: list, batch_size: int):
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]


class Post(BaseModel):
    user_id: int = Field(..., gt=0, alias="userId")
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1, max_length=1000)


async def fetch(client: httpx.AsyncClient, path: str, retry: int = 3, backoff_factor: float = 0.1) -> dict:
    for i in range(retry):
        try:
            resp = await client.get(path)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            print(f"HTTP error: {e}")
            await asyncio.sleep(backoff_factor * (1 << i))
    raise Exception(f"Request failed after {retry} retries")


async def fetch_posts(post_ids: list[int], concurrency: int = 5) -> list[Post]:
    if concurrency < 1:
        raise ValueError("concurrency must be >= 1")

    posts = []
    timeout = httpx.Timeout(15, connect=5)
    async with httpx.AsyncClient(
        base_url="https://jsonplaceholder.typicode.com", timeout=timeout
    ) as client:
        semaphore = asyncio.Semaphore(concurrency)

        async def limited_fetch(post_id: int) -> dict:
            async with semaphore:
                return await fetch(client, f"/posts/{post_id}")
        responses = await asyncio.gather(
            *(limited_fetch(post_id) for post_id in post_ids), return_exceptions=True
        )
        for post_id, response in zip(post_ids, responses):
            if isinstance(response, Exception):
                print(f"Error: post {post_id} failed, {type(response).__name__}: {response}")
                continue
            post = Post(**response)
            posts.append(post)
        return posts


if __name__ == "__main__":
    asyncio.run(fetch_posts([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 99999]))
