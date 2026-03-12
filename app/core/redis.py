from redis.asyncio import Redis

from app.core.config import Settings

_REDIS_CLIENT: Redis | None = None


async def open_redis_client(settings: Settings) -> None:
    global _REDIS_CLIENT
    if _REDIS_CLIENT is not None:
        return
    _REDIS_CLIENT = Redis.from_url(settings.redis_url, decode_responses=True)
    await _REDIS_CLIENT.ping()


async def close_redis_client() -> None:
    global _REDIS_CLIENT
    if _REDIS_CLIENT is None:
        return
    await _REDIS_CLIENT.close()
    _REDIS_CLIENT = None


def get_redis_client() -> Redis:
    if _REDIS_CLIENT is None:
        raise RuntimeError("Redis client is not initialized.")
    return _REDIS_CLIENT
