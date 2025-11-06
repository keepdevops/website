from typing import Optional
from core.email_interface import EmailProviderInterface
from config import settings
import logging

logger = logging.getLogger(__name__)


def get_email_provider() -> EmailProviderInterface:
    """
    Get email provider instance based on configuration.
    
    Returns:
        EmailProviderInterface implementation
    
    Raises:
        ValueError: If provider not configured or unknown
    """
    provider_name = getattr(settings, 'email_provider', 'sendgrid')
    
    if provider_name == "sendgrid":
        api_key = getattr(settings, 'sendgrid_api_key', None)
        if not api_key:
            raise ValueError("SendGrid API key not configured")
        
        from email_providers.sendgrid import SendGridEmailProvider
        return SendGridEmailProvider(
            api_key=api_key,
            default_from_email=getattr(settings, 'email_from', 'noreply@yoursaas.com')
        )
    
    elif provider_name == "mailgun":
        api_key = getattr(settings, 'mailgun_api_key', None)
        domain = getattr(settings, 'mailgun_domain', None)
        
        if not api_key or not domain:
            raise ValueError("Mailgun API key and domain required")
        
        from email_providers.mailgun import MailgunEmailProvider
        return MailgunEmailProvider(
            api_key=api_key,
            domain=domain,
            default_from_email=getattr(settings, 'email_from', 'noreply@yoursaas.com'),
            eu_region=getattr(settings, 'mailgun_eu_region', False)
        )
    
    elif provider_name == "postmark":
        api_key = getattr(settings, 'postmark_api_key', None)
        if not api_key:
            raise ValueError("Postmark API key not configured")
        
        from email_providers.postmark import PostmarkEmailProvider
        return PostmarkEmailProvider(
            api_key=api_key,
            default_from_email=getattr(settings, 'email_from', 'noreply@yoursaas.com'),
            message_stream=getattr(settings, 'postmark_message_stream', 'outbound')
        )
    
    elif provider_name == "aws_ses":
        region = getattr(settings, 'aws_ses_region', 'us-east-1')
        
        from email_providers.aws_ses import AWSSESEmailProvider
        return AWSSESEmailProvider(
            region=region,
            default_from_email=getattr(settings, 'email_from', 'noreply@yoursaas.com'),
            configuration_set=getattr(settings, 'aws_ses_configuration_set', None)
        )
    
    elif provider_name == "resend":
        api_key = getattr(settings, 'resend_api_key', None)
        if not api_key:
            raise ValueError("Resend API key not configured")
        
        from email_providers.resend import ResendEmailProvider
        return ResendEmailProvider(
            api_key=api_key,
            default_from_email=getattr(settings, 'email_from', 'noreply@yoursaas.com')
        )
    
    # Future providers can be added here
    else:
        raise ValueError(f"Unknown email provider: {provider_name}")

