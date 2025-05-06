import asyncio
from typing import Iterable, Awaitable, Any

async def gather_with_concurrency(concurrency:int,*aws:Iterable[Awaitable[Any]])->list[Any]:
    sem = asyncio.Semaphore(concurrency)
    async def wrap(coro):
        async with sem:
            return await coro
    return await asyncio.gather(*[wrap(a) for a in aws])
