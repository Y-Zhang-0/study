import functools
import time
import asyncio
from pydantic import BaseModel, Field, ValidationError
class BookEntry(BaseModel):
    book_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    authors: list[str] = Field(default_factory=list)
    rating: float | None = Field(default=None, ge=0, le=10)

def parse_book(raws: list[dict]) -> list[BookEntry]:
    books: list[BookEntry] = []
    for index, book in enumerate(raws):
        try:
            books.append(BookEntry(**book))
        except ValidationError as e:
            print(f"第{index+1}行解析失败: {e}")   
    return books

def async_time(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} Time taken: {(end - start):.2f} seconds")
        return result
    return wrapper

@async_time
async def async_function():
    await asyncio.sleep(1)
    print("Async function completed")

@async_time
async def fetch_book(book_id):
    await asyncio.sleep(1)
    return {"book_id": book_id ,"title": "三国演义", "price": 59.9, "authors": ["罗贯中"], "rating": 9.5} 

@async_time
async def fetch_book_gather(id_list):
    task_list = []
    for id in id_list:
        task_list.append(fetch_book(id))
    book_list = await asyncio.gather(*task_list)
    return parse_book(book_list)

async def main():
    await async_function()
    start = time.time()
    await fetch_book(1)
    await fetch_book(2)
    await fetch_book(3)
    end = time.time()
    print(f"顺序 ≈ {(end - start):.2f}")
    start = time.time()
    await fetch_book_gather([1,2,3])
    end = time.time()
    print(f"并发 ≈ {(end - start):.2f}")
asyncio.run(main())


