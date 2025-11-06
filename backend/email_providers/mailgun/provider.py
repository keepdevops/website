from typing import List, Dict, Any, Optional
import httpx
from core.email_interface import (
    EmailProviderInterface,
    EmailMessage,
    EmailResult,
    BulkEmailResult
)
import logging

logger = logging.getLogger(__name__)


class MailgunEmailProvider(EmailProviderInterface):
    """Mailgun email provider implementation"""
    
    def __init__(
        self,
        api_key: str,
        domain: str,
        default_from_email: str = "noreply@yoursaas.com",
        eu_region: bool = False
    ):
        self.api_key = api_key
        self.domain = domain
        self.default_from_email = default_from_email
        
        # Mailgun has US and EU endpoints
        base_url = "api.eu.mailgun.net" if eu_region else "api.mailgun.net"
        self.base_url = f"https://{base_url}/v3/{domain}"
    
    @property
    def provider_name(self) -> str:
        return "mailgun"
    
    def validate_config(self) -> bool:
        """Validate Mailgun configuration"""
        try:
            # Test by getting domain info
            response = httpx.get(
                f"https://api.mailgun.net/v3/domains/{self.domain}",
                auth=("api", self.api_key),
                timeout=10
            )
            valid = response.status_code == 200
            if valid:
                logger.info("Mailgun configuration is valid")
            return valid
        except Exception as e:
            logger.error(f"Mailgun config validation failed: {str(e)}")
            return False
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Send email via Mailgun"""
        try:
            async with httpx.AsyncClient() as client:
                # Build form data
                data = {
                    "from": message.from_email or self.default_from_email,
                    "to": message.to,
                    "subject": message.subject,
                    "text": message.text_content
                }
                
                if message.html_content:
                    data["html"] = message.html_content
                
                if message.reply_to:
                    data["h:Reply-To"] = message.reply_to
                
                if message.cc:
                    data["cc"] = message.cc
                
                if message.bcc:
                    data["bcc"] = message.bcc
                
                # Add tags
                if message.tags:
                    data["o:tag"] = message.tags
                
                # Add custom variables
                if message.metadata:
                    for key, value in message.metadata.items():
                        data[f"v:{key}"] = str(value)
                
                # Send request
                response = await client.post(
                    f"{self.base_url}/messages",
                    auth=("api", self.api_key),
                    data=data,
                    timeout=30
                )
                
                success = response.status_code == 200
                response_data = response.json() if success else {}
                
                logger.info(f"Mailgun email sent to {message.to}, status: {response.status_code}")
                
                return EmailResult(
                    success=success,
                    message_id=response_data.get("id"),
                    error=None if success else response.text,
                    provider_response=response_data
                )
        
        except Exception as e:
            logger.error(f"Mailgun error: {str(e)}")
            return EmailResult(success=False, error=str(e))
    
    async def send_bulk(self, messages: List[EmailMessage]) -> BulkEmailResult:
        """Send multiple emails via Mailgun"""
        sent = 0
        failed = 0
        errors = []
        
        for message in messages:
            result = await self.send_email(message)
            if result.success:
                sent += 1
            else:
                failed += 1
                if result.error:
                    errors.append(result.error)
        
        return BulkEmailResult(sent=sent, failed=failed, total=len(messages), errors=errors)
    
    async def send_template(
        self,
        template_id: str,
        to: List[str],
        variables: Dict[str, Any],
        from_email: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> EmailResult:
        """Send email using Mailgun template"""
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "from": from_email or self.default_from_email,
                    "to": to,
                    "template": template_id,
                }
                
                # Add template variables
                for key, value in variables.items():
                    data[f"v:{key}"] = str(value)
                
                if tags:
                    data["o:tag"] = tags
                
                response = await client.post(
                    f"{self.base_url}/messages",
                    auth=("api", self.api_key),
                    data=data,
                    timeout=30
                )
                
                success = response.status_code == 200
                response_data = response.json() if success else {}
                
                return EmailResult(
                    success=success,
                    message_id=response_data.get("id"),
                    error=None if success else response.text
                )
        
        except Exception as e:
            logger.error(f"Mailgun template error: {str(e)}")
            return EmailResult(success=False, error=str(e))

