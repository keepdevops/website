from typing import List, Optional, Dict, Any
from core.email_interface import (
    EmailProviderInterface,
    EmailMessage,
    EmailResult
)
from core.email_provider_factory import get_email_provider
from email_providers.templates import EmailTemplateManager
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """High-level email service using pluggable providers"""
    
    def __init__(self, provider: EmailProviderInterface):
        self.provider = provider
        self.template_manager = EmailTemplateManager()
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send a simple email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            content: Plain text content
            html_content: Optional HTML content
            from_email: Optional sender email
        
        Returns:
            True if sent successfully
        """
        message = EmailMessage(
            to=[to_email],
            subject=subject,
            text_content=content,
            html_content=html_content,
            from_email=from_email
        )
        
        result = await self.provider.send_email(message)
        
        if result.success:
            logger.info(f"Email sent to {to_email} via {self.provider.provider_name}")
        else:
            logger.error(f"Failed to send email to {to_email}: {result.error}")
        
        return result.success
    
    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        content: str,
        html_content: Optional[str] = None
    ) -> Dict[str, int]:
        """Send bulk emails to multiple recipients"""
        messages = []
        for recipient in recipients:
            messages.append(EmailMessage(
                to=[recipient],
                subject=subject,
                text_content=content,
                html_content=html_content
            ))
        
        result = await self.provider.send_bulk(messages)
        
        return {
            "sent": result.sent,
            "failed": result.failed,
            "total": result.total
        }
    
    async def send_transactional_email(
        self,
        to_email: str,
        template_name: str,
        variables: Dict[str, Any]
    ) -> bool:
        """
        Send transactional email using template.
        
        Args:
            to_email: Recipient email
            template_name: Template name (e.g., 'welcome', 'password_reset')
            variables: Template variables
        
        Returns:
            True if sent successfully
        """
        try:
            rendered = self.template_manager.render(template_name, variables)
            
            message = EmailMessage(
                to=[to_email],
                subject=rendered["subject"],
                text_content=rendered["text"],
                html_content=rendered.get("html"),
                tags=[template_name]
            )
            
            result = await self.provider.send_email(message)
            return result.success
        
        except Exception as e:
            logger.error(f"Error sending transactional email: {str(e)}")
            return False


def get_email_service() -> EmailService:
    """Get EmailService instance with configured provider"""
    provider = get_email_provider()
    return EmailService(provider)



