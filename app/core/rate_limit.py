from fastapi import HTTPException, status

from app.core.redis import get_redis_client


async def enforce_rate_limit(key: str, limit: int, window_seconds: int) -> None:
    redis = get_redis_client()
    namespaced_key = f'rate_limit:{key}'
    current = await redis.incr(namespaced_key)
    if current == 1:
        await redis.expire(namespaced_key, window_seconds)
    if int(current) > limit:
        ttl = await redis.ttl(namespaced_key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                'message': 'Rate limit exceeded.',
                'limit': limit,
                'window_seconds': window_seconds,
                'retry_after_seconds': max(int(ttl or 0), 0),
            },
        )


async def enforce_multiple_rate_limits(rules: list[tuple[str, int, int]]) -> None:
    for key, limit, window_seconds in rules:
        await enforce_rate_limit(key, limit=limit, window_seconds=window_seconds)
