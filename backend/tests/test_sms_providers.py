"""
Tests for SMS provider implementations.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from core.sms_interface import SMSProviderInterface
from sms_providers.twilio.provider import TwilioSMSProvider
from sms_providers.vonage.provider import VonageSMSProvider
from sms_providers.aws_sns.provider import AWSSNSSMSProvider
from sms_providers.messagebird.provider import MessageBirdSMSProvider
from sms_providers.console.provider import ConsoleSMSProvider
from core.sms_provider_factory import get_sms_provider


class TestSMSInterface:
    """Test SMS provider interface"""
    
    def test_interface_methods_exist(self):
        """Verify all required methods exist"""
        required = ['send_sms', 'send_verification_code', 'verify_phone', 'get_message_status']
        for method in required:
            assert hasattr(SMSProviderInterface, method)


@pytest.mark.asyncio
class TestConsoleSMSProvider:
    """Test console SMS provider"""
    
    async def test_send_sms(self):
        """Test sending SMS to console"""
        provider = ConsoleSMSProvider()
        
        result = await provider.send_sms("+1234567890", "Test message")
        
        assert result["status"] == "delivered"
        assert result["to"] == "+1234567890"
        assert "message_id" in result
    
    async def test_send_verification_code(self):
        """Test sending verification code"""
        provider = ConsoleSMSProvider()
        
        result = await provider.send_verification_code("+1234567890", "123456")
        
        assert result["status"] == "delivered"
        assert "message_id" in result
    
    async def test_verify_phone_success(self):
        """Test successful phone verification"""
        provider = ConsoleSMSProvider()
        
        await provider.send_verification_code("+1234567890", "123456")
        result = await provider.verify_phone("+1234567890", "123456")
        
        assert result is True
    
    async def test_verify_phone_failure(self):
        """Test failed phone verification"""
        provider = ConsoleSMSProvider()
        
        await provider.send_verification_code("+1234567890", "123456")
        result = await provider.verify_phone("+1234567890", "wrong_code")
        
        assert result is False


@pytest.mark.asyncio
class TestTwilioSMSProvider:
    """Test Twilio SMS provider"""
    
    @patch('sms_providers.twilio.provider.Client')
    async def test_send_sms(self, mock_client_class):
        """Test Twilio SMS sending"""
        mock_message = Mock()
        mock_message.sid = "SM123456"
        mock_message.status = "queued"
        mock_message.from_ = "+1234567890"
        mock_message.price = "0.0075"
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client
        
        provider = TwilioSMSProvider("account_sid", "auth_token", "+1234567890")
        result = await provider.send_sms("+0987654321", "Test")
        
        assert result["message_id"] == "SM123456"
        assert result["status"] == "queued"


@pytest.mark.asyncio
class TestVonageSMSProvider:
    """Test Vonage SMS provider"""
    
    @patch('sms_providers.vonage.provider.httpx.AsyncClient')
    async def test_send_sms(self, mock_client_class):
        """Test Vonage SMS sending"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "messages": [{
                "message-id": "123",
                "status": "0",
                "message-price": "0.05"
            }]
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        provider = VonageSMSProvider("api_key", "api_secret")
        result = await provider.send_sms("+1234567890", "Test")
        
        assert result["message_id"] == "123"


@pytest.mark.asyncio
class TestAWSSNSSMSProvider:
    """Test AWS SNS SMS provider"""
    
    @patch('sms_providers.aws_sns.provider.boto3')
    async def test_send_sms(self, mock_boto3):
        """Test AWS SNS SMS sending"""
        mock_client = Mock()
        mock_client.publish.return_value = {"MessageId": "msg123"}
        mock_boto3.client.return_value = mock_client
        
        provider = AWSSNSSMSProvider("key_id", "secret_key")
        result = await provider.send_sms("+1234567890", "Test")
        
        assert result["message_id"] == "msg123"
        assert result["status"] == "sent"


@pytest.mark.asyncio
class TestMessageBirdSMSProvider:
    """Test MessageBird SMS provider"""
    
    @patch('sms_providers.messagebird.provider.httpx.AsyncClient')
    async def test_send_sms(self, mock_client_class):
        """Test MessageBird SMS sending"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "mb123",
            "status": "sent",
            "originator": "MessageBird",
            "pricing": {"amount": 0.05}
        }
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        provider = MessageBirdSMSProvider("api_key")
        result = await provider.send_sms("+1234567890", "Test")
        
        assert result["message_id"] == "mb123"


def test_sms_provider_factory():
    """Test SMS provider factory"""
    with patch('core.sms_provider_factory.settings') as mock_settings:
        mock_settings.sms_provider = "console"
        
        provider = get_sms_provider()
        assert isinstance(provider, ConsoleSMSProvider)
    
    with patch('core.sms_provider_factory.settings') as mock_settings:
        mock_settings.sms_provider = "unsupported"
        
        with pytest.raises(ValueError, match="Unsupported SMS provider"):
            get_sms_provider()

