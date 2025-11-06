import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from core.cache_interface import CacheProviderInterface
from cache_providers.memory import MemoryCacheProvider


class TestCacheInterface:
    """Test cache provider interface"""
    
    @pytest.mark.asyncio
    async def test_memory_provider_basic_operations(self):
        """Test basic cache operations with memory provider"""
        cache = MemoryCacheProvider()
        
        # Set and get
        await cache.set("test_key", "test_value")
        value = await cache.get("test_key")
        assert value == "test_value"
        
        # Exists
        exists = await cache.exists("test_key")
        assert exists is True
        
        # Delete
        deleted = await cache.delete("test_key")
        assert deleted is True
        
        # Check deleted
        value = await cache.get("test_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_memory_provider_json(self):
        """Test JSON operations"""
        cache = MemoryCacheProvider()
        
        data = {"user": "test", "count": 42}
        await cache.set_json("json_key", data)
        
        retrieved = await cache.get_json("json_key")
        assert retrieved == data
    
    @pytest.mark.asyncio
    async def test_memory_provider_increment(self):
        """Test increment operation"""
        cache = MemoryCacheProvider()
        
        # Increment from 0
        value = await cache.increment("counter")
        assert value == 1
        
        # Increment by 5
        value = await cache.increment("counter", 5)
        assert value == 6
    
    @pytest.mark.asyncio
    async def test_memory_provider_expiration(self):
        """Test expiration"""
        cache = MemoryCacheProvider()
        
        # Set with very short expiration
        await cache.set("temp_key", "temp_value", expiration=1)
        
        # Should exist immediately
        exists = await cache.exists("temp_key")
        assert exists is True
        
        # Wait for expiration
        import asyncio
        await asyncio.sleep(1.1)
        
        # Should be expired
        value = await cache.get("temp_key")
        assert value is None


class TestRedisProvider:
    """Test Redis cache provider"""
    
    @pytest.mark.asyncio
    @patch('redis.asyncio.from_url')
    async def test_redis_get(self, mock_redis):
        """Test Redis get operation"""
        from cache_providers.redis import RedisCacheProvider
        
        mock_client = AsyncMock()
        mock_client.get.return_value = "test_value"
        mock_redis.return_value = mock_client
        
        provider = RedisCacheProvider()
        value = await provider.get("test_key")
        
        assert value == "test_value"
        mock_client.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    @patch('redis.asyncio.from_url')
    async def test_redis_set(self, mock_redis):
        """Test Redis set operation"""
        from cache_providers.redis import RedisCacheProvider
        
        mock_client = AsyncMock()
        mock_client.set.return_value = True
        mock_redis.return_value = mock_client
        
        provider = RedisCacheProvider()
        result = await provider.set("test_key", "test_value", 3600)
        
        assert result is True
        mock_client.set.assert_called_once_with("test_key", "test_value", ex=3600)
    
    def test_provider_name(self):
        """Test Redis provider name"""
        from cache_providers.redis import RedisCacheProvider
        
        provider = RedisCacheProvider()
        assert provider.provider_name == "redis"


class TestUpstashProvider:
    """Test Upstash cache provider"""
    
    @pytest.mark.asyncio
    async def test_upstash_get(self):
        """Test Upstash get operation"""
        from cache_providers.upstash import UpstashCacheProvider
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "test_value"}
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            provider = UpstashCacheProvider(
                redis_rest_url="https://test.upstash.io",
                redis_rest_token="test_token"
            )
            
            value = await provider.get("test_key")
            assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_upstash_set(self):
        """Test Upstash set operation"""
        from cache_providers.upstash import UpstashCacheProvider
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "OK"}
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            provider = UpstashCacheProvider(
                redis_rest_url="https://test.upstash.io",
                redis_rest_token="test_token"
            )
            
            result = await provider.set("test_key", "test_value")
            assert result is True
    
    def test_provider_name(self):
        """Test Upstash provider name"""
        from cache_providers.upstash import UpstashCacheProvider
        
        provider = UpstashCacheProvider("url", "token")
        assert provider.provider_name == "upstash"


class TestCacheService:
    """Test high-level Cache service"""
    
    @pytest.mark.asyncio
    async def test_cache_service_with_memory_provider(self):
        """Test Cache service using memory provider"""
        from core.cache import Cache
        from cache_providers.memory import MemoryCacheProvider
        
        provider = MemoryCacheProvider()
        cache = Cache(provider)
        
        # Test set and get
        await cache.set("key1", "value1")
        value = await cache.get("key1")
        assert value == "value1"
        
        # Test JSON
        data = {"test": "data"}
        await cache.set_json("json_key", data)
        retrieved = await cache.get_json("json_key")
        assert retrieved == data
        
        # Test increment
        count = await cache.increment("counter")
        assert count == 1
        
        count = await cache.increment("counter", 5)
        assert count == 6

