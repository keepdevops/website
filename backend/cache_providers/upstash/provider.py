from typing import Optional
import httpx
from core.cache_interface import CacheProviderInterface
import logging

logger = logging.getLogger(__name__)


class UpstashCacheProvider(CacheProviderInterface):
    """Upstash Redis cache provider (serverless, pay-per-request)"""
    
    def __init__(self, redis_rest_url: str, redis_rest_token: str):
        self.base_url = redis_rest_url.rstrip('/')
        self.token = redis_rest_token
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @property
    def provider_name(self) -> str:
        return "upstash"
    
    async def _execute(self, *command: str):
        """Execute Redis command via REST API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=list(command),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("result")
                
                logger.error(f"Upstash error: {response.status_code} {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Upstash request error: {str(e)}")
            return None
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Upstash"""
        result = await self._execute("GET", key)
        return result
    
    async def set(self, key: str, value: str, expiration: int = 3600) -> bool:
        """Set value in Upstash with expiration"""
        result = await self._execute("SET", key, value, "EX", str(expiration))
        return result == "OK"
    
    async def delete(self, key: str) -> bool:
        """Delete key from Upstash"""
        result = await self._execute("DEL", key)
        return result == 1
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Upstash"""
        result = await self._execute("EXISTS", key)
        return result == 1
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment value in Upstash"""
        result = await self._execute("INCRBY", key, str(amount))
        return int(result) if result is not None else 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        result = await self._execute("EXPIRE", key, str(seconds))
        return result == 1
    
    async def close(self):
        """Close connection (no-op for REST API)"""
        pass

