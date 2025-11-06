from typing import List, Dict, Any, Optional
import httpx
from core.email_interface import (
    EmailProviderInterface,
    EmailMessage,
    EmailResult,
    BulkEmailResult
)
import logging
import base64

logger = logging.getLogger(__name__)


class PostmarkEmailProvider(EmailProviderInterface):
    """Postmark email provider implementation"""
    
    def __init__(
        self,
        api_key: str,
        default_from_email: str = "noreply@yoursaas.com",
        message_stream: str = "outbound"
    ):
        self.api_key = api_key
        self.default_from_email = default_from_email
        self.message_stream = message_stream
        self.base_url = "https://api.postmarkapp.com"
    
    @property
    def provider_name(self) -> str:
        return "postmark"
    
    def validate_config(self) -> bool:
        """Validate Postmark configuration"""
        try:
            # Test API key by getting server details
            response = httpx.get(
                f"{self.base_url}/server",
                headers={"X-Postmark-Server-Token": self.api_key},
                timeout=10
            )
            valid = response.status_code == 200
            if valid:
                logger.info("Postmark configuration is valid")
            return valid
        except Exception as e:
            logger.error(f"Postmark config validation failed: {str(e)}")
            return False
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Send email via Postmark"""
        try:
            async with httpx.AsyncClient() as client:
                # Build request payload
                payload = {
                    "From": message.from_email or self.default_from_email,
                    "To": ", ".join(message.to),
                    "Subject": message.subject,
                    "TextBody": message.text_content,
                    "MessageStream": self.message_stream
                }
                
                if message.html_content:
                    payload["HtmlBody"] = message.html_content
                
                if message.reply_to:
                    payload["ReplyTo"] = message.reply_to
                
                if message.cc:
                    payload["Cc"] = ", ".join(message.cc)
                
                if message.bcc:
                    payload["Bcc"] = ", ".join(message.bcc)
                
                # Add tags
                if message.tags:
                    payload["Tag"] = message.tags[0]  # Postmark only supports one tag
                
                # Add metadata
                if message.metadata:
                    payload["Metadata"] = message.metadata
                
                # Add attachments
                if message.attachments:
                    attachments = []
                    for attachment in message.attachments:
                        attachments.append({
                            "Name": attachment.filename,
                            "Content": base64.b64encode(attachment.content).decode(),
                            "ContentType": attachment.content_type
                        })
                    payload["Attachments"] = attachments
                
                # Send request
                response = await client.post(
                    f"{self.base_url}/email",
                    headers={
                        "X-Postmark-Server-Token": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30
                )
                
                success = response.status_code == 200
                response_data = response.json() if success else {}
                
                logger.info(f"Postmark email sent to {message.to}, status: {response.status_code}")
                
                return EmailResult(
                    success=success,
                    message_id=response_data.get("MessageID"),
                    error=None if success else response_data.get("Message"),
                    provider_response=response_data
                )
        
        except Exception as e:
            logger.error(f"Postmark error: {str(e)}")
            return EmailResult(success=False, error=str(e))
    
    async def send_bulk(self, messages: List[EmailMessage]) -> BulkEmailResult:
        """Send multiple emails via Postmark batch API"""
        # Postmark supports batch sending, but for simplicity we'll send individually
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
        """Send email using Postmark template"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "From": from_email or self.default_from_email,
                    "To": ", ".join(to),
                    "TemplateId": int(template_id),
                    "TemplateModel": variables,
                    "MessageStream": self.message_stream
                }
                
                if tags:
                    payload["Tag"] = tags[0]
                
                response = await client.post(
                    f"{self.base_url}/email/withTemplate",
                    headers={
                        "X-Postmark-Server-Token": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30
                )
                
                success = response.status_code == 200
                response_data = response.json() if success else {}
                
                return EmailResult(
                    success=success,
                    message_id=response_data.get("MessageID"),
                    error=None if success else response_data.get("Message")
                )
        
        except Exception as e:
            logger.error(f"Postmark template error: {str(e)}")
            return EmailResult(success=False, error=str(e))

