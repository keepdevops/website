from typing import Optional
from core.cache_interface import CacheProviderInterface
from config import settings
import logging

logger = logging.getLogger(__name__)


def get_cache_provider() -> CacheProviderInterface:
    """
    Get cache provider instance based on configuration.
    
    Returns:
        CacheProviderInterface implementation
    
    Raises:
        ValueError: If provider not configured or unknown
    """
    provider_name = getattr(settings, 'cache_provider', 'redis')
    
    if provider_name == "redis":
        redis_url = getattr(settings, 'redis_url', 'redis://localhost:6379')
        
        from cache_providers.redis import RedisCacheProvider
        return RedisCacheProvider(redis_url=redis_url)
    
    elif provider_name == "upstash":
        rest_url = getattr(settings, 'upstash_redis_rest_url', None)
        rest_token = getattr(settings, 'upstash_redis_rest_token', None)
        
        if not rest_url or not rest_token:
            raise ValueError("Upstash REST URL and token required")
        
        from cache_providers.upstash import UpstashCacheProvider
        return UpstashCacheProvider(
            redis_rest_url=rest_url,
            redis_rest_token=rest_token
        )
    
    elif provider_name == "memory":
        from cache_providers.memory import MemoryCacheProvider
        return MemoryCacheProvider()
    
    # Future providers:
    # elif provider_name == "memcached":
    #     from cache_providers.memcached import MemcachedCacheProvider
    #     return MemcachedCacheProvider(...)
    # elif provider_name == "cloudflare_kv":
    #     from cache_providers.cloudflare_kv import CloudflareKVCacheProvider
    #     return CloudflareKVCacheProvider(...)
    
    else:
        raise ValueError(f"Unknown cache provider: {provider_name}")

