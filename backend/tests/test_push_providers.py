"""
Tests for push notification provider implementations.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from core.push_notification_interface import PushNotificationInterface
from push_notification_providers.onesignal.provider import OneSignalPushProvider
from push_notification_providers.firebase.provider import FirebasePushProvider
from push_notification_providers.aws_sns_push.provider import AWSSNSPushProvider
from push_notification_providers.pusher.provider import PusherBeamsPushProvider
from push_notification_providers.webpush.provider import WebPushProvider
from core.push_notification_factory import get_push_notification_provider


class TestPushNotificationInterface:
    """Test push notification interface"""
    
    def test_interface_methods_exist(self):
        """Verify all required methods exist"""
        required = [
            'send_notification', 'send_to_segment', 'subscribe_device',
            'unsubscribe_device', 'get_notification_status'
        ]
        for method in required:
            assert hasattr(PushNotificationInterface, method)


@pytest.mark.asyncio
class TestOneSignalPushProvider:
    """Test OneSignal push provider"""
    
    @patch('push_notification_providers.onesignal.provider.httpx.AsyncClient')
    async def test_send_notification(self, mock_client_class):
        """Test OneSignal send notification"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "notif123", "recipients": 1}
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        provider = OneSignalPushProvider("app_id", "api_key")
        result = await provider.send_notification(
            user_ids=["user123"],
            title="Test",
            body="Test message"
        )
        
        assert result["notification_id"] == "notif123"
        assert result["recipients"] == 1


@pytest.mark.asyncio
class TestFirebasePushProvider:
    """Test Firebase push provider"""
    
    @patch('push_notification_providers.firebase.provider.initialize_app')
    @patch('push_notification_providers.firebase.provider.credentials')
    @patch('push_notification_providers.firebase.provider.messaging')
    async def test_send_notification(self, mock_messaging, mock_creds, mock_init):
        """Test Firebase send notification"""
        mock_messaging.send_multicast.return_value = Mock(success_count=1, failure_count=0)
        
        provider = FirebasePushProvider("creds.json")
        await provider.subscribe_device("user123", "device_token", "ios")
        
        result = await provider.send_notification(
            user_ids=["user123"],
            title="Test",
            body="Message"
        )
        
        assert result["recipients"] == 1


@pytest.mark.asyncio
class TestAWSSNSPushProvider:
    """Test AWS SNS Push provider"""
    
    @patch('push_notification_providers.aws_sns_push.provider.boto3')
    async def test_subscribe_device(self, mock_boto3):
        """Test AWS SNS device subscription"""
        mock_client = Mock()
        mock_client.create_platform_endpoint.return_value = {"EndpointArn": "arn:aws:sns:endpoint"}
        mock_boto3.client.return_value = mock_client
        
        provider = AWSSNSPushProvider("platform_arn")
        result = await provider.subscribe_device("user123", "device_token", "ios")
        
        assert result is True


@pytest.mark.asyncio
class TestPusherBeamsPushProvider:
    """Test Pusher Beams push provider"""
    
    @patch('push_notification_providers.pusher.provider.httpx.AsyncClient')
    async def test_send_to_segment(self, mock_client_class):
        """Test Pusher Beams segment send"""
        mock_response = Mock()
        mock_response.json.return_value = {"publishId": "pub123"}
        mock_response.raise_for_status = Mock()
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        provider = PusherBeamsPushProvider("instance_id", "secret_key")
        result = await provider.send_to_segment("premium_users", "Title", "Body")
        
        assert result["publishId"] == "pub123"


@pytest.mark.asyncio
class TestWebPushProvider:
    """Test Web Push provider"""
    
    @patch('push_notification_providers.webpush.provider.webpush')
    async def test_send_notification(self, mock_webpush):
        """Test Web Push send notification"""
        provider = WebPushProvider("public_key", "private_key")
        
        # Register a subscription first
        subscription = '{"endpoint":"https://push.example.com","keys":{"p256dh":"key","auth":"auth"}}'
        await provider.subscribe_device("user123", subscription, "web")
        
        result = await provider.send_notification(
            user_ids=["user123"],
            title="Test",
            body="Message"
        )
        
        assert result["recipients"] >= 0


def test_push_notification_factory():
    """Test push notification factory"""
    with patch('core.push_notification_factory.settings') as mock_settings:
        mock_settings.push_notification_provider = "unsupported"
        
        with pytest.raises(ValueError, match="Unsupported push notification provider"):
            get_push_notification_provider()

