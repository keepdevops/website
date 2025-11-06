from typing import Optional
from core.cache_interface import CacheProviderInterface
from core.cache_provider_factory import get_cache_provider
import logging

logger = logging.getLogger(__name__)

# Legacy support - keep old import working
_provider_instance: Optional[CacheProviderInterface] = None


async def get_redis_client():
    """Legacy function - now returns cache provider"""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = get_cache_provider()
    return _provider_instance


class Cache:
    """High-level cache service using pluggable providers"""
    
    def __init__(self, provider: Optional[CacheProviderInterface] = None):
        self.provider = provider or get_cache_provider()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        return await self.provider.get(key)
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from cache"""
        return await self.provider.get_json(key)
    
    async def set(self, key: str, value: str, expiration: int = 3600) -> bool:
        """Set value in cache"""
        return await self.provider.set(key, value, expiration)
    
    async def set_json(self, key: str, value: dict, expiration: int = 3600) -> bool:
        """Set JSON value in cache"""
        return await self.provider.set_json(key, value, expiration)
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return await self.provider.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.provider.exists(key)
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value"""
        return await self.provider.increment(key, amount)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        return await self.provider.expire(key, seconds)


def get_cache() -> Cache:
    """Get Cache instance with configured provider"""
    return Cache()



