import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from core.monitoring_interface import (
    MonitoringProviderInterface,
    ErrorContext,
    ErrorSeverity
)
from monitoring_providers.console import ConsoleMonitoringProvider


class MockMonitoringProvider(MonitoringProviderInterface):
    """Mock monitoring provider for testing"""
    
    def __init__(self):
        self.logged_errors = []
        self.logged_messages = []
        self.logged_events = []
        self.user_contexts = []
        self.performance_metrics = []
    
    @property
    def provider_name(self) -> str:
        return "mock"
    
    async def log_error(self, error, context=None, severity=ErrorSeverity.ERROR):
        self.logged_errors.append((error, context, severity))
        return True
    
    async def log_message(self, message, level=ErrorSeverity.INFO, extra=None):
        self.logged_messages.append((message, level, extra))
        return True
    
    async def log_event(self, event_name, properties=None):
        self.logged_events.append((event_name, properties))
        return True
    
    async def set_user_context(self, user_id, user_data=None):
        self.user_contexts.append((user_id, user_data))
        return True
    
    async def track_performance(self, operation, duration_ms, metadata=None):
        self.performance_metrics.append((operation, duration_ms, metadata))
        return True


class TestMonitoringInterface:
    """Test monitoring interface"""
    
    @pytest.mark.asyncio
    async def test_log_error(self):
        """Test logging errors"""
        provider = MockMonitoringProvider()
        
        error = ValueError("Test error")
        context = ErrorContext(
            user_id="user_123",
            endpoint="/api/test"
        )
        
        result = await provider.log_error(error, context, ErrorSeverity.ERROR)
        
        assert result is True
        assert len(provider.logged_errors) == 1
        assert provider.logged_errors[0][0] == error
    
    @pytest.mark.asyncio
    async def test_log_event(self):
        """Test logging custom events"""
        provider = MockMonitoringProvider()
        
        result = await provider.log_event(
            "user_signup",
            {"source": "web", "plan": "premium"}
        )
        
        assert result is True
        assert len(provider.logged_events) == 1
        assert provider.logged_events[0][0] == "user_signup"
    
    @pytest.mark.asyncio
    async def test_set_user_context(self):
        """Test setting user context"""
        provider = MockMonitoringProvider()
        
        result = await provider.set_user_context(
            "user_123",
            {"email": "test@example.com", "name": "Test User"}
        )
        
        assert result is True
        assert len(provider.user_contexts) == 1
    
    @pytest.mark.asyncio
    async def test_track_performance(self):
        """Test performance tracking"""
        provider = MockMonitoringProvider()
        
        result = await provider.track_performance(
            "database_query",
            45.5,
            {"query": "SELECT * FROM users"}
        )
        
        assert result is True
        assert len(provider.performance_metrics) == 1
        assert provider.performance_metrics[0][1] == 45.5


class TestConsoleProvider:
    """Test console monitoring provider"""
    
    @pytest.mark.asyncio
    async def test_log_error(self):
        """Test console error logging"""
        provider = ConsoleMonitoringProvider()
        
        error = ValueError("Test error")
        result = await provider.log_error(error)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_log_message(self):
        """Test console message logging"""
        provider = ConsoleMonitoringProvider()
        
        result = await provider.log_message("Test message", ErrorSeverity.INFO)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_log_event(self):
        """Test console event logging"""
        provider = ConsoleMonitoringProvider()
        
        result = await provider.log_event("test_event", {"key": "value"})
        
        assert result is True
    
    def test_provider_name(self):
        """Test provider name"""
        provider = ConsoleMonitoringProvider()
        assert provider.provider_name == "console"


class TestSentryProvider:
    """Test Sentry monitoring provider"""
    
    @pytest.mark.asyncio
    @patch('sentry_sdk.init')
    @patch('sentry_sdk.capture_exception')
    async def test_sentry_log_error(self, mock_capture, mock_init):
        """Test Sentry error logging"""
        from monitoring_providers.sentry import SentryMonitoringProvider
        
        provider = SentryMonitoringProvider(dsn="https://test@sentry.io/123")
        
        error = ValueError("Test error")
        result = await provider.log_error(error)
        
        assert result is True
        mock_capture.assert_called_once()
    
    @patch('sentry_sdk.init')
    def test_provider_name(self, mock_init):
        """Test Sentry provider name"""
        from monitoring_providers.sentry import SentryMonitoringProvider
        
        provider = SentryMonitoringProvider(dsn="https://test@sentry.io/123")
        assert provider.provider_name == "sentry"


class TestMonitoringService:
    """Test monitoring service with multiple providers"""
    
    @pytest.mark.asyncio
    async def test_multi_provider_error_logging(self):
        """Test logging to multiple providers"""
        from core.monitoring_middleware import MonitoringService
        
        provider1 = MockMonitoringProvider()
        provider2 = MockMonitoringProvider()
        
        service = MonitoringService(providers=[provider1, provider2])
        
        error = ValueError("Test error")
        await service.log_error(error)
        
        # Both providers should receive the error
        assert len(provider1.logged_errors) == 1
        assert len(provider2.logged_errors) == 1
    
    @pytest.mark.asyncio
    async def test_multi_provider_event_logging(self):
        """Test logging events to multiple providers"""
        from core.monitoring_middleware import MonitoringService
        
        provider1 = MockMonitoringProvider()
        provider2 = MockMonitoringProvider()
        
        service = MonitoringService(providers=[provider1, provider2])
        
        await service.log_event("test_event", {"key": "value"})
        
        # Both providers should receive the event
        assert len(provider1.logged_events) == 1
        assert len(provider2.logged_events) == 1

