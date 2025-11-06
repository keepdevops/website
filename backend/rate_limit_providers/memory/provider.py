"""
In-memory rate limit provider implementation.
For testing and development - not suitable for production with multiple instances.
"""
from typing import Optional, Dict
from datetime import datetime, timedelta
from collections import defaultdict
from core.rate_limit_interface import RateLimitProviderInterface, RateLimitInfo


class MemoryRateLimitProvider(RateLimitProviderInterface):
    """In-memory rate limiting for testing"""
    
    def __init__(self):
        self.counts: Dict[str, int] = defaultdict(int)
        self.timestamps: Dict[str, datetime] = {}
    
    def _clean_expired(self, key: str, window: int):
        """Remove expired entries"""
        if key in self.timestamps:
            elapsed = (datetime.utcnow() - self.timestamps[key]).total_seconds()
            if elapsed >= window:
                self.counts[key] = 0
                self.timestamps[key] = datetime.utcnow()
    
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> RateLimitInfo:
        """Check rate limit using fixed window"""
        self._clean_expired(key, window)
        
        count = self.counts.get(key, 0)
        allowed = count < limit
        remaining = max(0, limit - count)
        
        now = datetime.utcnow()
        if key in self.timestamps:
            reset_at = self.timestamps[key] + timedelta(seconds=window)
        else:
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
        self._clean_expired(key, window)
        
        if key not in self.timestamps:
            self.timestamps[key] = datetime.utcnow()
        
        self.counts[key] += amount
        return self.counts[key]
    
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
        if key in self.counts:
            del self.counts[key]
        if key in self.timestamps:
            del self.timestamps[key]
        return True
    
    async def get_reset_time(
        self,
        key: str,
        window: int
    ) -> Optional[datetime]:
        """Get reset time for key"""
        if key in self.timestamps:
            return self.timestamps[key] + timedelta(seconds=window)
        return None

