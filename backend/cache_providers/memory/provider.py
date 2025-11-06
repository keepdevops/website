from typing import Optional, Dict
from datetime import datetime, timedelta
from core.cache_interface import CacheProviderInterface
import logging

logger = logging.getLogger(__name__)


class MemoryCacheProvider(CacheProviderInterface):
    """In-memory cache provider for testing and development"""
    
    def __init__(self):
        self._cache: Dict[str, tuple[str, Optional[datetime]]] = {}
    
    @property
    def provider_name(self) -> str:
        return "memory"
    
    def _is_expired(self, key: str) -> bool:
        """Check if key has expired"""
        if key not in self._cache:
            return True
        
        _, expiry = self._cache[key]
        if expiry is None:
            return False
        
        if datetime.utcnow() > expiry:
            del self._cache[key]
            return True
        
        return False
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from memory"""
        if self._is_expired(key):
            return None
        
        value, _ = self._cache.get(key, (None, None))
        return value
    
    async def set(self, key: str, value: str, expiration: int = 3600) -> bool:
        """Set value in memory with expiration"""
        try:
            expiry = datetime.utcnow() + timedelta(seconds=expiration) if expiration > 0 else None
            self._cache[key] = (value, expiry)
            return True
        except Exception as e:
            logger.error(f"Memory cache set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from memory"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in memory"""
        if self._is_expired(key):
            return False
        return key in self._cache
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value in memory"""
        try:
            current = await self.get(key)
            new_value = int(current or 0) + amount
            await self.set(key, str(new_value))
            return new_value
        except Exception as e:
            logger.error(f"Memory cache increment error: {str(e)}")
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on existing key"""
        if key not in self._cache:
            return False
        
        value, _ = self._cache[key]
        expiry = datetime.utcnow() + timedelta(seconds=seconds)
        self._cache[key] = (value, expiry)
        return True
    
    async def clear(self):
        """Clear all cache (useful for testing)"""
        self._cache.clear()
        logger.info("Memory cache cleared")
    
    async def close(self):
        """Close connection (no-op for memory)"""
        pass

