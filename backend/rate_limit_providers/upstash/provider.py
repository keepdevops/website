"""
Upstash rate limit provider implementation.
Uses Upstash REST API for serverless-friendly rate limiting.
"""
import httpx
from typing import Optional
from datetime import datetime, timedelta
from core.rate_limit_interface import RateLimitProviderInterface, RateLimitInfo


class UpstashRateLimitProvider(RateLimitProviderInterface):
    """Upstash REST API based rate limiting"""
    
    def __init__(self, rest_url: str, rest_token: str):
        self.rest_url = rest_url.rstrip('/')
        self.rest_token = rest_token
        self.headers = {"Authorization": f"Bearer {rest_token}"}
    
    async def _execute_command(self, *args):
        """Execute Upstash Redis command via REST API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.rest_url,
                headers=self.headers,
                json=args
            )
            response.raise_for_status()
            return response.json().get('result')
    
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> RateLimitInfo:
        """Check rate limit using fixed window"""
        rate_key = f"rate_limit:{key}"
        
        # Get current count
        count = await self._execute_command("GET", rate_key)
        count = int(count) if count else 0
        
        allowed = count < limit
        remaining = max(0, limit - count)
        now = datetime.utcnow()
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
        rate_key = f"rate_limit:{key}"
        
        # Increment counter
        count = await self._execute_command("INCRBY", rate_key, amount)
        
        # Set expiration if new key
        if count == amount:
            await self._execute_command("EXPIRE", rate_key, window)
        
        return count
    
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
        rate_key = f"rate_limit:{key}"
        await self._execute_command("DEL", rate_key)
        return True
    
    async def get_reset_time(
        self,
        key: str,
        window: int
    ) -> Optional[datetime]:
        """Get reset time for key"""
        rate_key = f"rate_limit:{key}"
        
        ttl = await self._execute_command("TTL", rate_key)
        if ttl and ttl > 0:
            return datetime.utcnow() + timedelta(seconds=ttl)
        
        return None

