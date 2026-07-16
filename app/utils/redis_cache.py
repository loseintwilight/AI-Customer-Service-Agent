"""Redis 工具类：缓存操作和对话历史管理"""

import json
from typing import Any, Optional
import redis.asyncio as aioredis

from app.config import settings

# Redis 连接池
_redis_pool: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """获取 Redis 连接实例"""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=10
        )
    return _redis_pool


class RedisCache:
    """Redis 缓存工具类"""

    @staticmethod
    async def get(key: str) -> Optional[str]:
        """获取缓存"""
        r = await get_redis()
        return await r.get(key)

    @staticmethod
    async def set(key: str, value: str, expire: int = 3600) -> None:
        """设置缓存"""
        r = await get_redis()
        await r.setex(key, expire, value)

    @staticmethod
    async def delete(key: str) -> bool:
        """删除缓存"""
        r = await get_redis()
        return bool(await r.delete(key))

    @staticmethod
    async def get_list(key: str) -> list[Any]:
        """获取列表缓存"""
        r = await get_redis()
        items = await r.lrange(key, 0, -1)
        return [json.loads(item) if isinstance(item, str) else item for item in items]

    @staticmethod
    async def push_to_list(key: str, value: Any) -> None:
        """向列表尾部添加元素"""
        r = await get_redis()
        await r.rpush(key, json.dumps(value, ensure_ascii=False))

    @staticmethod
    async def get_chat_history(session_id: str) -> list[dict]:
        """获取对话历史"""
        key = f"spring_ai_alibaba_chat_memory:{session_id}"
        return await RedisCache.get_list(key)

    @staticmethod
    async def save_chat_message(session_id: str, message: dict) -> None:
        """保存对话消息"""
        key = f"spring_ai_alibaba_chat_memory:{session_id}"
        await RedisCache.push_to_list(key, message)

    @staticmethod
    async def delete_chat_history(session_id: str) -> bool:
        """删除对话历史"""
        key = f"spring_ai_alibaba_chat_memory:{session_id}"
        return await RedisCache.delete(key)