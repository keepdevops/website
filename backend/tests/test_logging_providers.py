"""
Tests for logging provider implementations.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, mock_open
from core.logging_interface import LoggingProviderInterface
from logging_providers.console.provider import ConsoleLoggingProvider
from logging_providers.json.provider import JSONLoggingProvider
from logging_providers.file.provider import FileLoggingProvider
from logging_providers.datadog.provider import DatadogLoggingProvider
from logging_providers.betterstack.provider import BetterStackLoggingProvider
from logging_providers.cloudwatch.provider import CloudWatchLoggingProvider
from core.logging_provider_factory import get_logging_provider


class TestLoggingInterface:
    """Test logging provider interface"""
    
    def test_interface_methods_exist(self):
        """Verify all required methods exist"""
        required = ['log_info', 'log_warning', 'log_error', 'log_debug', 'log_with_level']
        for method in required:
            assert hasattr(LoggingProviderInterface, method)


@pytest.mark.asyncio
class TestConsoleLoggingProvider:
    """Test console logging provider"""
    
    async def test_log_info(self, capsys):
        """Test info logging"""
        provider = ConsoleLoggingProvider(colorize=False)
        
        await provider.log_info("Test info message", {"user_id": "123"})
        
        captured = capsys.readouterr()
        assert "INFO" in captured.out
        assert "Test info message" in captured.out
        assert "user_id=123" in captured.out
    
    async def test_log_error_with_exception(self, capsys):
        """Test error logging with exception"""
        provider = ConsoleLoggingProvider(colorize=False)
        error = ValueError("Test error")
        
        await provider.log_error("Error occurred", error=error)
        
        captured = capsys.readouterr()
        assert "ERROR" in captured.err
        assert "Error occurred" in captured.err
        assert "ValueError" in captured.err


@pytest.mark.asyncio
class TestJSONLoggingProvider:
    """Test JSON logging provider"""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=True)
    async def test_log_info(self, mock_exists, mock_makedirs, mock_file):
        """Test JSON info logging"""
        provider = JSONLoggingProvider("test.json")
        
        await provider.log_info("Test message", {"key": "value"})
        
        mock_file.assert_called()


@pytest.mark.asyncio
class TestFileLoggingProvider:
    """Test file logging provider"""
    
    @patch('logging.handlers.RotatingFileHandler')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=True)
    async def test_log_warning(self, mock_exists, mock_makedirs, mock_handler):
        """Test file warning logging"""
        provider = FileLoggingProvider("test.log")
        
        await provider.log_warning("Warning message")
        
        # Logger should be created
        assert provider.logger is not None


@pytest.mark.asyncio
class TestDatadogLoggingProvider:
    """Test Datadog logging provider"""
    
    @patch('logging_providers.datadog.provider.httpx.AsyncClient')
    async def test_log_error(self, mock_client_class):
        """Test Datadog error logging"""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        provider = DatadogLoggingProvider("api_key", "app_key")
        error = RuntimeError("Test error")
        
        await provider.log_error("Error occurred", error=error, context={"request_id": "123"})
        
        mock_client.post.assert_called_once()


@pytest.mark.asyncio
class TestBetterStackLoggingProvider:
    """Test Better Stack logging provider"""
    
    @patch('logging_providers.betterstack.provider.httpx.AsyncClient')
    async def test_log_info(self, mock_client_class):
        """Test Better Stack info logging"""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock()
        mock_client_class.return_value = mock_client
        
        provider = BetterStackLoggingProvider("source_token")
        
        await provider.log_info("Test info")
        
        mock_client.post.assert_called_once()


@pytest.mark.asyncio
class TestCloudWatchLoggingProvider:
    """Test CloudWatch logging provider"""
    
    @patch('logging_providers.cloudwatch.provider.boto3')
    async def test_log_debug(self, mock_boto3):
        """Test CloudWatch debug logging"""
        mock_client = Mock()
        mock_client.create_log_group = Mock(side_effect=ClientError(
            {'Error': {'Code': 'ResourceAlreadyExistsException'}}, 'create_log_group'
        ))
        mock_client.create_log_stream = Mock()
        mock_client.put_log_events = Mock(return_value={'nextSequenceToken': 'token123'})
        mock_boto3.client.return_value = mock_client
        
        provider = CloudWatchLoggingProvider()
        
        await provider.log_debug("Debug message")
        
        mock_client.put_log_events.assert_called_once()


def test_logging_provider_factory():
    """Test logging provider factory"""
    with patch('core.logging_provider_factory.settings') as mock_settings:
        mock_settings.logging_provider = "console"
        
        provider = get_logging_provider()
        assert isinstance(provider, ConsoleLoggingProvider)
    
    with patch('core.logging_provider_factory.settings') as mock_settings:
        mock_settings.logging_provider = "unsupported"
        
        with pytest.raises(ValueError, match="Unsupported logging provider"):
            get_logging_provider()


from botocore.exceptions import ClientError

