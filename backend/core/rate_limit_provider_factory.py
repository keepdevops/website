"""
Factory for creating rate limit provider instances.
Supports Redis, Upstash, and in-memory providers.
"""
from typing import Optional
from core.rate_limit_interface import RateLimitProviderInterface
from config import settings


def get_rate_limit_provider(
    provider_name: Optional[str] = None
) -> RateLimitProviderInterface:
    """
    Factory function to get the configured rate limit provider.
    
    Args:
        provider_name: Override the default provider from settings
        
    Returns:
        RateLimitProviderInterface implementation
        
    Raises:
        ValueError: If provider is not supported
    """
    provider = provider_name or settings.rate_limit_provider
    
    if provider == "redis":
        from rate_limit_providers.redis.provider import RedisRateLimitProvider
        return RedisRateLimitProvider(redis_url=settings.redis_url)
    
    elif provider == "upstash":
        from rate_limit_providers.upstash.provider import UpstashRateLimitProvider
        return UpstashRateLimitProvider(
            rest_url=settings.upstash_redis_rest_url,
            rest_token=settings.upstash_redis_rest_token
        )
    
    elif provider == "memory":
        from rate_limit_providers.memory.provider import MemoryRateLimitProvider
        return MemoryRateLimitProvider()
    
    else:
        raise ValueError(
            f"Unsupported rate limit provider: {provider}. "
            f"Supported: redis, upstash, memory"
        )

