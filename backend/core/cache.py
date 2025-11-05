import redis.asyncio as redis
from typing import Optional
from functools import lru_cache
import json
from config import settings

_redis_client: Optional[redis.Redis] = None

async def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client

class Cache:
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = await get_redis_client()
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        client = await self._get_client()
        return await client.get(key)
    
    async def get_json(self, key: str) -> Optional[dict]:
        value = await self.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: str, expiration: int = 3600) -> bool:
        client = await self._get_client()
        return await client.set(key, value, ex=expiration)
    
    async def set_json(self, key: str, value: dict, expiration: int = 3600) -> bool:
        return await self.set(key, json.dumps(value), expiration)
    
    async def delete(self, key: str) -> bool:
        client = await self._get_client()
        return await client.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        client = await self._get_client()
        return await client.exists(key) > 0
    
    async def increment(self, key: str, amount: int = 1) -> int:
        client = await self._get_client()
        return await client.incrby(key, amount)
    
    async def expire(self, key: str, seconds: int) -> bool:
        client = await self._get_client()
        return await client.expire(key, seconds)

def get_cache() -> Cache:
    return Cache()

