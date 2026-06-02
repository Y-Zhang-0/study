from pydantic import BaseModel, Field
import httpx
import asyncio

def batch_iter(items: list, batch_size: int):
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

class Post(BaseModel):
    user_id: int = Field(..., gt=0, alias="userId")
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=100)
    body: str = Field(..., min_length=1, max_length=1000)

async def fetch(client: httpx.AsyncClient, path: str) -> dict:
    resp = await client.get(path)
    resp.raise_for_status()
    return resp.json()

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

if __name__ == "__main__":
    asyncio.run(fetch_posts([1,2,3,4,5,6,7,8,9,10,99999]))