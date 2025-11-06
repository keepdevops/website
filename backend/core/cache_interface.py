from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import json


class CacheProviderInterface(ABC):
    """Abstract interface for cache providers (Redis, Upstash, Memcached, etc.)"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Value as string or None if not found
        """
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, expiration: int = 3600) -> bool:
        """
        Set value in cache with expiration.
        
        Args:
            key: Cache key
            value: Value to store (string)
            expiration: TTL in seconds (default 3600 = 1 hour)
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if key was deleted
        """
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
        
        Returns:
            True if key exists
        """
        pass
    
    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment numeric value in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
        
        Returns:
            New value after increment
        """
        pass
    
    @abstractmethod
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration on existing key.
        
        Args:
            key: Cache key
            seconds: TTL in seconds
        
        Returns:
            True if expiration was set
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this cache provider"""
        pass
    
    # Helper methods (default implementations using core methods)
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from cache"""
        value = await self.get(key)
        return json.loads(value) if value else None
    
    async def set_json(self, key: str, value: dict, expiration: int = 3600) -> bool:
        """Set JSON value in cache"""
        return await self.set(key, json.dumps(value), expiration)

