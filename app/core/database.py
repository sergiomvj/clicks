from typing import Final

import asyncpg
from asyncpg import Pool

from app.core.config import Settings

_DATABASE_POOL: Pool | None = None
_POOL_MIN_SIZE: Final[int] = 2
_POOL_MAX_SIZE: Final[int] = 10


async def open_database_pool(settings: Settings) -> None:
    global _DATABASE_POOL
    if _DATABASE_POOL is not None:
        return
    _DATABASE_POOL = await asyncpg.create_pool(
        dsn=settings.database_url_asyncpg,
        min_size=_POOL_MIN_SIZE,
        max_size=_POOL_MAX_SIZE,
        timeout=10,
    )


async def close_database_pool() -> None:
    global _DATABASE_POOL
    if _DATABASE_POOL is None:
        return
    await _DATABASE_POOL.close()
    _DATABASE_POOL = None


def get_database_pool() -> Pool:
    if _DATABASE_POOL is None:
        raise RuntimeError("Database pool is not initialized.")
    return _DATABASE_POOL
