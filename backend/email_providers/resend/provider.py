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


class ResendEmailProvider(EmailProviderInterface):
    """Resend email provider implementation"""
    
    def __init__(self, api_key: str, default_from_email: str = "noreply@yoursaas.com"):
        self.api_key = api_key
        self.default_from_email = default_from_email
        self.base_url = "https://api.resend.com"
    
    @property
    def provider_name(self) -> str:
        return "resend"
    
    def validate_config(self) -> bool:
        """Validate Resend configuration"""
        try:
            # Test by getting API keys
            response = httpx.get(
                f"{self.base_url}/api-keys",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            valid = response.status_code == 200
            if valid:
                logger.info("Resend configuration is valid")
            return valid
        except Exception as e:
            logger.error(f"Resend config validation failed: {str(e)}")
            return False
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Send email via Resend"""
        try:
            async with httpx.AsyncClient() as client:
                # Build payload
                payload = {
                    "from": message.from_email or self.default_from_email,
                    "to": message.to,
                    "subject": message.subject,
                    "text": message.text_content
                }
                
                if message.html_content:
                    payload["html"] = message.html_content
                
                if message.reply_to:
                    payload["reply_to"] = message.reply_to
                
                if message.cc:
                    payload["cc"] = message.cc
                
                if message.bcc:
                    payload["bcc"] = message.bcc
                
                # Add tags
                if message.tags:
                    payload["tags"] = [{"name": tag, "value": "true"} for tag in message.tags]
                
                # Add attachments
                if message.attachments:
                    attachments = []
                    for attachment in message.attachments:
                        attachments.append({
                            "filename": attachment.filename,
                            "content": base64.b64encode(attachment.content).decode()
                        })
                    payload["attachments"] = attachments
                
                # Send request
                response = await client.post(
                    f"{self.base_url}/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30
                )
                
                success = response.status_code in [200, 201]
                response_data = response.json() if success else {}
                
                logger.info(f"Resend email sent to {message.to}, status: {response.status_code}")
                
                return EmailResult(
                    success=success,
                    message_id=response_data.get("id"),
                    error=None if success else response_data.get("message"),
                    provider_response=response_data
                )
        
        except Exception as e:
            logger.error(f"Resend error: {str(e)}")
            return EmailResult(success=False, error=str(e))
    
    async def send_bulk(self, messages: List[EmailMessage]) -> BulkEmailResult:
        """Send multiple emails via Resend batch API"""
        try:
            async with httpx.AsyncClient() as client:
                # Build batch payload
                batch_payload = []
                for message in messages:
                    email_data = {
                        "from": message.from_email or self.default_from_email,
                        "to": message.to,
                        "subject": message.subject,
                        "text": message.text_content
                    }
                    
                    if message.html_content:
                        email_data["html"] = message.html_content
                    
                    batch_payload.append(email_data)
                
                # Send batch request
                response = await client.post(
                    f"{self.base_url}/emails/batch",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=batch_payload,
                    timeout=60
                )
                
                if response.status_code in [200, 201]:
                    response_data = response.json()
                    sent = len(response_data.get("data", []))
                    failed = len(messages) - sent
                    
                    return BulkEmailResult(
                        sent=sent,
                        failed=failed,
                        total=len(messages)
                    )
                else:
                    return BulkEmailResult(
                        sent=0,
                        failed=len(messages),
                        total=len(messages),
                        errors=[response.text]
                    )
        
        except Exception as e:
            logger.error(f"Resend bulk error: {str(e)}")
            return BulkEmailResult(
                sent=0,
                failed=len(messages),
                total=len(messages),
                errors=[str(e)]
            )
    
    async def send_template(
        self,
        template_id: str,
        to: List[str],
        variables: Dict[str, Any],
        from_email: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> EmailResult:
        """Send email using Resend template (React Email)"""
        # Note: Resend uses React Email templates
        # Template rendering happens server-side with React
        logger.warning("Resend template support requires React Email setup")
        return EmailResult(success=False, error="Template not implemented for Resend")

