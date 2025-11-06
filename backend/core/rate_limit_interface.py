"""
Abstract interface for rate limiting providers.
Defines operations for checking and managing rate limits.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime


class RateLimitInfo:
    """Rate limit information for a key"""
    
    def __init__(
        self,
        allowed: bool,
        limit: int,
        remaining: int,
        reset_at: datetime,
        retry_after: Optional[int] = None
    ):
        self.allowed = allowed
        self.limit = limit
        self.remaining = remaining
        self.reset_at = reset_at
        self.retry_after = retry_after  # Seconds until reset


class RateLimitProviderInterface(ABC):
    """Abstract interface for rate limit providers"""
    
    @abstractmethod
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> RateLimitInfo:
        """
        Check if request is within rate limit.
        
        Args:
            key: Unique identifier (user_id, ip, endpoint)
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            RateLimitInfo with allowed status and metadata
        """
        pass
    
    @abstractmethod
    async def increment(
        self,
        key: str,
        window: int,
        amount: int = 1
    ) -> int:
        """
        Increment rate limit counter.
        
        Args:
            key: Unique identifier
            window: Time window in seconds
            amount: Amount to increment by
            
        Returns:
            Current count after increment
        """
        pass
    
    @abstractmethod
    async def get_remaining(
        self,
        key: str,
        limit: int,
        window: int
    ) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Unique identifier
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            Remaining requests
        """
        pass
    
    @abstractmethod
    async def reset(
        self,
        key: str
    ) -> bool:
        """
        Reset rate limit for a key.
        
        Args:
            key: Unique identifier
            
        Returns:
            True if reset successful
        """
        pass
    
    @abstractmethod
    async def get_reset_time(
        self,
        key: str,
        window: int
    ) -> Optional[datetime]:
        """
        Get time when rate limit will reset.
        
        Args:
            key: Unique identifier
            window: Time window in seconds
            
        Returns:
            Reset datetime or None
        """
        pass

