from fastapi import FastAPI
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis


async def get_redis_client():
    redis = aioredis.from_url("redis://redis_app:6379/0")
    return redis


# для запуска и завершения фоновых задач
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = await get_redis_client()  # Инициализация Redis
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
