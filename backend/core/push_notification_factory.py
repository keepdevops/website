"""
Factory for creating push notification provider instances.
Supports OneSignal, Firebase, AWS SNS Push, Pusher Beams, and Web Push.
"""
from typing import Optional
from core.push_notification_interface import PushNotificationInterface
from config import settings


def get_push_notification_provider(
    provider_name: Optional[str] = None
) -> PushNotificationInterface:
    """
    Factory function to get the configured push notification provider.
    
    Args:
        provider_name: Override the default provider from settings
        
    Returns:
        PushNotificationInterface implementation
        
    Raises:
        ValueError: If provider is not supported
    """
    provider = provider_name or settings.push_notification_provider
    
    if provider == "onesignal":
        from push_notification_providers.onesignal.provider import OneSignalPushProvider
        return OneSignalPushProvider(
            app_id=settings.onesignal_app_id,
            api_key=settings.onesignal_api_key
        )
    
    elif provider == "firebase":
        from push_notification_providers.firebase.provider import FirebasePushProvider
        return FirebasePushProvider(
            credentials_path=settings.firebase_credentials_path,
            project_id=settings.firebase_project_id
        )
    
    elif provider == "aws_sns_push":
        from push_notification_providers.aws_sns_push.provider import AWSSNSPushProvider
        return AWSSNSPushProvider(
            platform_application_arn=settings.aws_sns_platform_application_arn,
            region=settings.aws_region
        )
    
    elif provider == "pusher":
        from push_notification_providers.pusher.provider import PusherBeamsPushProvider
        return PusherBeamsPushProvider(
            instance_id=settings.pusher_beams_instance_id,
            secret_key=settings.pusher_beams_secret_key
        )
    
    elif provider == "webpush":
        from push_notification_providers.webpush.provider import WebPushProvider
        return WebPushProvider(
            vapid_public_key=settings.vapid_public_key,
            vapid_private_key=settings.vapid_private_key,
            vapid_subject=settings.vapid_subject
        )
    
    else:
        raise ValueError(
            f"Unsupported push notification provider: {provider}. "
            f"Supported: onesignal, firebase, aws_sns_push, pusher, webpush"
        )

