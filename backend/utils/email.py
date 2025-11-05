from typing import List, Optional
import httpx
from config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = settings.email_provider_api_key
        self.from_email = "noreply@yoursaas.com"
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None
    ) -> bool:
        try:
            logger.info(f"Sending email to {to_email} with subject: {subject}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        content: str,
        html_content: Optional[str] = None
    ) -> dict:
        sent_count = 0
        failed_count = 0
        
        for recipient in recipients:
            success = await self.send_email(recipient, subject, content, html_content)
            if success:
                sent_count += 1
            else:
                failed_count += 1
        
        return {
            "sent": sent_count,
            "failed": failed_count,
            "total": len(recipients)
        }
    
    async def send_transactional_email(
        self,
        to_email: str,
        template_name: str,
        variables: dict
    ) -> bool:
        templates = {
            "welcome": {
                "subject": "Welcome to Our Platform!",
                "content": "Hello {name}, welcome aboard!"
            },
            "subscription_created": {
                "subject": "Subscription Confirmed",
                "content": "Your subscription is now active."
            },
            "payment_failed": {
                "subject": "Payment Failed",
                "content": "We couldn't process your payment."
            },
            "subscription_cancelled": {
                "subject": "Subscription Cancelled",
                "content": "Your subscription has been cancelled."
            }
        }
        
        template = templates.get(template_name)
        if not template:
            logger.error(f"Template not found: {template_name}")
            return False
        
        subject = template["subject"]
        content = template["content"].format(**variables)
        
        return await self.send_email(to_email, subject, content)

def get_email_service() -> EmailService:
    return EmailService()

