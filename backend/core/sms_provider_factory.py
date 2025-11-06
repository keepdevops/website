"""
Factory for creating SMS provider instances.
Supports Twilio, Vonage, AWS SNS, MessageBird, and Console providers.
"""
from typing import Optional
from core.sms_interface import SMSProviderInterface
from config import settings


def get_sms_provider(provider_name: Optional[str] = None) -> SMSProviderInterface:
    """
    Factory function to get the configured SMS provider.
    
    Args:
        provider_name: Override the default provider from settings
        
    Returns:
        SMSProviderInterface implementation
        
    Raises:
        ValueError: If provider is not supported
    """
    provider = provider_name or settings.sms_provider
    
    if provider == "twilio":
        from sms_providers.twilio.provider import TwilioSMSProvider
        return TwilioSMSProvider(
            account_sid=settings.twilio_account_sid,
            auth_token=settings.twilio_auth_token,
            from_number=settings.twilio_phone_number
        )
    
    elif provider == "vonage":
        from sms_providers.vonage.provider import VonageSMSProvider
        return VonageSMSProvider(
            api_key=settings.vonage_api_key,
            api_secret=settings.vonage_api_secret,
            from_number=settings.vonage_phone_number
        )
    
    elif provider == "aws_sns":
        from sms_providers.aws_sns.provider import AWSSNSSMSProvider
        return AWSSNSSMSProvider(
            access_key_id=settings.aws_access_key_id,
            secret_access_key=settings.aws_secret_access_key,
            region=settings.aws_region
        )
    
    elif provider == "messagebird":
        from sms_providers.messagebird.provider import MessageBirdSMSProvider
        return MessageBirdSMSProvider(
            api_key=settings.messagebird_api_key,
            from_number=settings.messagebird_phone_number
        )
    
    elif provider == "console":
        from sms_providers.console.provider import ConsoleSMSProvider
        return ConsoleSMSProvider()
    
    else:
        raise ValueError(
            f"Unsupported SMS provider: {provider}. "
            f"Supported: twilio, vonage, aws_sns, messagebird, console"
        )

