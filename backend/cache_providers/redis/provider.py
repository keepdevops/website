import redis.asyncio as redis
from typing import Optional
from core.cache_interface import CacheProviderInterface
import logging

logger = logging.getLogger(__name__)


class RedisCacheProvider(CacheProviderInterface):
    """Redis cache provider implementation"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
    
    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client"""
        if self._client is None:
            self._client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info(f"Redis client connected to {self.redis_url}")
        return self._client
    
    @property
    def provider_name(self) -> str:
        return "redis"
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        try:
            client = await self._get_client()
            return await client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    async def set(self, key: str, value: str, expiration: int = 3600) -> bool:
        """Set value in Redis with expiration"""
        try:
            client = await self._get_client()
            return await client.set(key, value, ex=expiration)
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            client = await self._get_client()
            return await client.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            client = await self._get_client()
            return await client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {str(e)}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment value in Redis"""
        try:
            client = await self._get_client()
            return await client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis increment error: {str(e)}")
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        try:
            client = await self._get_client()
            return await client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis expire error: {str(e)}")
            return False
    
    async def close(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            logger.info("Redis connection closed")

