"""
Tests for rate limit provider implementations.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from core.rate_limit_interface import RateLimitProviderInterface, RateLimitInfo
from rate_limit_providers.redis.provider import RedisRateLimitProvider
from rate_limit_providers.upstash.provider import UpstashRateLimitProvider
from rate_limit_providers.memory.provider import MemoryRateLimitProvider
from core.rate_limit_provider_factory import get_rate_limit_provider


class TestRateLimitInterface:
    """Test rate limit provider interface"""
    
    def test_interface_methods_exist(self):
        """Verify all required methods exist"""
        required = ['check_rate_limit', 'increment', 'get_remaining', 'reset', 'get_reset_time']
        for method in required:
            assert hasattr(RateLimitProviderInterface, method)


@pytest.mark.asyncio
class TestMemoryRateLimitProvider:
    """Test in-memory rate limit provider"""
    
    async def test_check_rate_limit_allowed(self):
        """Test rate limit check when under limit"""
        provider = MemoryRateLimitProvider()
        
        info = await provider.check_rate_limit("test_key", limit=10, window=60)
        
        assert info.allowed is True
        assert info.limit == 10
        assert info.remaining == 10
    
    async def test_increment(self):
        """Test incrementing rate limit counter"""
        provider = MemoryRateLimitProvider()
        
        count = await provider.increment("test_key", window=60)
        assert count == 1
        
        count = await provider.increment("test_key", window=60, amount=2)
        assert count == 3
    
    async def test_rate_limit_exceeded(self):
        """Test rate limit when exceeded"""
        provider = MemoryRateLimitProvider()
        
        # Increment to limit
        for _ in range(5):
            await provider.increment("test_key", window=60)
        
        info = await provider.check_rate_limit("test_key", limit=5, window=60)
        
        assert info.allowed is False
        assert info.remaining == 0
    
    async def test_reset(self):
        """Test resetting rate limit"""
        provider = MemoryRateLimitProvider()
        
        await provider.increment("test_key", window=60)
        success = await provider.reset("test_key")
        
        assert success is True
        info = await provider.check_rate_limit("test_key", limit=10, window=60)
        assert info.remaining == 10


@pytest.mark.asyncio
class TestRedisRateLimitProvider:
    """Test Redis rate limit provider"""
    
    @patch('rate_limit_providers.redis.provider.redis')
    async def test_check_rate_limit(self, mock_redis_module):
        """Test Redis rate limit check"""
        mock_client = AsyncMock()
        mock_client.zremrangebyscore = AsyncMock()
        mock_client.zcard = AsyncMock(return_value=5)
        mock_redis_module.from_url.return_value = mock_client
        
        provider = RedisRateLimitProvider("redis://localhost")
        info = await provider.check_rate_limit("test_key", limit=10, window=60)
        
        assert info.allowed is True
        assert info.remaining == 5
    
    @patch('rate_limit_providers.redis.provider.redis')
    async def test_increment(self, mock_redis_module):
        """Test Redis increment"""
        mock_client = AsyncMock()
        mock_client.zadd = AsyncMock()
        mock_client.expire = AsyncMock()
        mock_client.zcard = AsyncMock(return_value=1)
        mock_redis_module.from_url.return_value = mock_client
        
        provider = RedisRateLimitProvider("redis://localhost")
        count = await provider.increment("test_key", window=60)
        
        assert count == 1
        mock_client.zadd.assert_called()


@pytest.mark.asyncio
class TestUpstashRateLimitProvider:
    """Test Upstash rate limit provider"""
    
    @patch('rate_limit_providers.upstash.provider.httpx.AsyncClient')
    async def test_check_rate_limit(self, mock_client_class):
        """Test Upstash rate limit check"""
        mock_response = Mock()
        mock_response.json.return_value = {"result": 5}
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        provider = UpstashRateLimitProvider("https://api.upstash.com", "token")
        info = await provider.check_rate_limit("test_key", limit=10, window=60)
        
        assert info.allowed is True
        assert info.remaining == 5


def test_rate_limit_provider_factory():
    """Test rate limit provider factory"""
    with patch('core.rate_limit_provider_factory.settings') as mock_settings:
        mock_settings.rate_limit_provider = "memory"
        
        provider = get_rate_limit_provider()
        assert isinstance(provider, MemoryRateLimitProvider)
    
    with patch('core.rate_limit_provider_factory.settings') as mock_settings:
        mock_settings.rate_limit_provider = "unsupported"
        
        with pytest.raises(ValueError, match="Unsupported rate limit provider"):
            get_rate_limit_provider()

