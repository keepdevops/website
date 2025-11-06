"""
Redis rate limit provider implementation.
Uses sliding window algorithm for accurate rate limiting.
"""
import redis.asyncio as redis
from typing import Optional
from datetime import datetime, timedelta
from core.rate_limit_interface import RateLimitProviderInterface, RateLimitInfo


class RedisRateLimitProvider(RateLimitProviderInterface):
    """Redis-based rate limiting with sliding window"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
    
    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client"""
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client
    
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> RateLimitInfo:
        """Check rate limit using sliding window"""
        client = await self._get_client()
        rate_key = f"rate_limit:{key}"
        
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window)
        
        # Remove old entries outside window
        await client.zremrangebyscore(
            rate_key,
            0,
            window_start.timestamp()
        )
        
        # Count requests in current window
        count = await client.zcard(rate_key)
        
        allowed = count < limit
        remaining = max(0, limit - count)
        reset_at = now + timedelta(seconds=window)
        retry_after = None if allowed else window
        
        return RateLimitInfo(
            allowed=allowed,
            limit=limit,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=retry_after
        )
    
    async def increment(
        self,
        key: str,
        window: int,
        amount: int = 1
    ) -> int:
        """Increment rate limit counter"""
        client = await self._get_client()
        rate_key = f"rate_limit:{key}"
        
        now = datetime.utcnow()
        
        # Add current request(s) with timestamp
        for _ in range(amount):
            await client.zadd(
                rate_key,
                {str(now.timestamp()): now.timestamp()}
            )
        
        # Set expiration
        await client.expire(rate_key, window)
        
        # Return current count
        return await client.zcard(rate_key)
    
    async def get_remaining(
        self,
        key: str,
        limit: int,
        window: int
    ) -> int:
        """Get remaining requests"""
        info = await self.check_rate_limit(key, limit, window)
        return info.remaining
    
    async def reset(self, key: str) -> bool:
        """Reset rate limit for key"""
        client = await self._get_client()
        rate_key = f"rate_limit:{key}"
        await client.delete(rate_key)
        return True
    
    async def get_reset_time(
        self,
        key: str,
        window: int
    ) -> Optional[datetime]:
        """Get reset time for key"""
        client = await self._get_client()
        rate_key = f"rate_limit:{key}"
        
        ttl = await client.ttl(rate_key)
        if ttl > 0:
            return datetime.utcnow() + timedelta(seconds=ttl)
        
        return None

