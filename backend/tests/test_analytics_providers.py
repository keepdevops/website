import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from core.analytics_interface import AnalyticsProviderInterface


class MockAnalyticsProvider(AnalyticsProviderInterface):
    """Mock analytics provider for testing"""
    
    def __init__(self):
        self.tracked_events = []
        self.tracked_pageviews = []
        self.identified_users = []
        self.tracked_revenue = []
    
    @property
    def provider_name(self) -> str:
        return "mock"
    
    async def track_event(self, event_name, user_id=None, properties=None):
        self.tracked_events.append((event_name, user_id, properties))
        return True
    
    async def track_page_view(self, user_id, page, properties=None):
        self.tracked_pageviews.append((user_id, page, properties))
        return True
    
    async def identify_user(self, user_id, traits=None):
        self.identified_users.append((user_id, traits))
        return True
    
    async def track_revenue(self, user_id, amount, currency="usd", properties=None):
        self.tracked_revenue.append((user_id, amount, currency, properties))
        return True


class TestAnalyticsInterface:
    """Test analytics interface"""
    
    @pytest.mark.asyncio
    async def test_track_event(self):
        """Test tracking events"""
        provider = MockAnalyticsProvider()
        
        result = await provider.track_event(
            "user_signup",
            user_id="user_123",
            properties={"plan": "premium"}
        )
        
        assert result is True
        assert len(provider.tracked_events) == 1
    
    @pytest.mark.asyncio
    async def test_identify_user(self):
        """Test user identification"""
        provider = MockAnalyticsProvider()
        
        result = await provider.identify_user(
            "user_123",
            traits={"email": "test@example.com"}
        )
        
        assert result is True
        assert len(provider.identified_users) == 1


class TestGoogleAnalyticsProvider:
    """Test Google Analytics provider"""
    
    @pytest.mark.asyncio
    async def test_track_event(self):
        """Test GA4 event tracking"""
        from analytics_providers.google_analytics import GoogleAnalyticsProvider
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            provider = GoogleAnalyticsProvider(
                measurement_id="G-XXXXXXXXXX",
                api_secret="secret"
            )
            
            result = await provider.track_event("test_event", "user_123")
            assert result is True


class TestPostHogProvider:
    """Test PostHog provider"""
    
    @pytest.mark.asyncio
    @patch('posthog.Posthog')
    async def test_track_event(self, mock_posthog):
        """Test PostHog event tracking"""
        from analytics_providers.posthog import PostHogAnalyticsProvider
        
        mock_client = MagicMock()
        mock_posthog.return_value = mock_client
        
        provider = PostHogAnalyticsProvider(api_key="test_key")
        
        result = await provider.track_event("test_event", "user_123")
        assert result is True
        mock_client.capture.assert_called_once()


class TestInternalAnalyticsProvider:
    """Test internal database analytics provider"""
    
    @pytest.mark.asyncio
    async def test_track_event(self):
        """Test internal event tracking"""
        from analytics_providers.internal import InternalAnalyticsProvider
        
        mock_db = AsyncMock()
        provider = InternalAnalyticsProvider(db=mock_db)
        
        result = await provider.track_event("test_event", "user_123", {"key": "value"})
        
        assert result is True
        mock_db.create.assert_called_once()

