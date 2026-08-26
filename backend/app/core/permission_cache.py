from typing import List, Optional
import uuid
from app.core.redis import get_redis_client


async def get_cached_user_permissions(user_id: uuid.UUID) -> Optional[List[str]]:
    """Retrieve cached permissions for a user from Redis."""
    try:
        redis = await get_redis_client()
        key = f"user_perms:{user_id}"
        exists = await redis.exists(key)
        if not exists:
            return None
        members = await redis.smembers(key)
        return [m for m in members if m != "__NONE__"]
    except Exception:
        return None


async def set_cached_user_permissions(user_id: uuid.UUID, permissions: List[str]) -> None:
    """Store user permissions in Redis set with 1 hour TTL."""
    try:
        redis = await get_redis_client()
        key = f"user_perms:{user_id}"
        await redis.delete(key)
        if permissions:
            await redis.sadd(key, *permissions)
        else:
            await redis.sadd(key, "__NONE__")
        await redis.expire(key, 3600)
    except Exception:
        pass


async def invalidate_cached_user_permissions(user_id: uuid.UUID) -> None:
    """Invalidate cached permissions for a user in Redis."""
    try:
        redis = await get_redis_client()
        key = f"user_perms:{user_id}"
        await redis.delete(key)
    except Exception:
        pass
