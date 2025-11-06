from typing import List, Dict, Any, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, Content, Personalization, Attachment
from core.email_interface import (
    EmailProviderInterface,
    EmailMessage,
    EmailResult,
    BulkEmailResult
)
import logging
import base64

logger = logging.getLogger(__name__)


class SendGridEmailProvider(EmailProviderInterface):
    """SendGrid email provider implementation"""
    
    def __init__(self, api_key: str, default_from_email: str = "noreply@yoursaas.com"):
        self.api_key = api_key
        self.default_from_email = default_from_email
        self.client = SendGridAPIClient(api_key)
    
    @property
    def provider_name(self) -> str:
        return "sendgrid"
    
    def validate_config(self) -> bool:
        """Validate SendGrid configuration"""
        try:
            # Test API key by checking sender verification
            self.client.client.verified_senders.get()
            logger.info("SendGrid configuration is valid")
            return True
        except Exception as e:
            logger.error(f"SendGrid config validation failed: {str(e)}")
            return False
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Send email via SendGrid"""
        try:
            mail = Mail()
            
            # Set from
            from_email = message.from_email or self.default_from_email
            mail.from_email = Email(from_email, message.from_name)
            
            # Set subject
            mail.subject = message.subject
            
            # Set content
            if message.html_content:
                mail.add_content(Content("text/html", message.html_content))
            mail.add_content(Content("text/plain", message.text_content))
            
            # Add recipients
            personalization = Personalization()
            for recipient in message.to:
                personalization.add_to(Email(recipient))
            
            if message.cc:
                for cc_email in message.cc:
                    personalization.add_cc(Email(cc_email))
            
            if message.bcc:
                for bcc_email in message.bcc:
                    personalization.add_bcc(Email(bcc_email))
            
            mail.add_personalization(personalization)
            
            # Add reply-to
            if message.reply_to:
                mail.reply_to = Email(message.reply_to)
            
            # Add attachments
            if message.attachments:
                for attachment in message.attachments:
                    sg_attachment = Attachment()
                    sg_attachment.file_content = base64.b64encode(attachment.content).decode()
                    sg_attachment.file_name = attachment.filename
                    sg_attachment.file_type = attachment.content_type
                    mail.add_attachment(sg_attachment)
            
            # Add custom args/metadata
            if message.metadata:
                for key, value in message.metadata.items():
                    mail.add_custom_arg(key, str(value))
            
            # Add tags/categories
            if message.tags:
                for tag in message.tags:
                    mail.add_category(tag)
            
            # Send
            response = self.client.send(mail)
            
            logger.info(f"SendGrid email sent to {message.to}, status: {response.status_code}")
            
            return EmailResult(
                success=response.status_code in [200, 201, 202],
                message_id=response.headers.get('X-Message-Id'),
                provider_response={"status_code": response.status_code}
            )
        
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return EmailResult(success=False, error=str(e))
    
    async def send_bulk(self, messages: List[EmailMessage]) -> BulkEmailResult:
        """Send multiple emails via SendGrid"""
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
        
        return BulkEmailResult(
            sent=sent,
            failed=failed,
            total=len(messages),
            errors=errors
        )
    
    async def send_template(
        self,
        template_id: str,
        to: List[str],
        variables: Dict[str, Any],
        from_email: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> EmailResult:
        """Send email using SendGrid dynamic template"""
        try:
            mail = Mail()
            mail.from_email = Email(from_email or self.default_from_email)
            mail.template_id = template_id
            
            personalization = Personalization()
            for recipient in to:
                personalization.add_to(Email(recipient))
            
            # Add template variables
            for key, value in variables.items():
                personalization.add_dynamic_template_data(key, value)
            
            mail.add_personalization(personalization)
            
            # Add tags
            if tags:
                for tag in tags:
                    mail.add_category(tag)
            
            response = self.client.send(mail)
            
            return EmailResult(
                success=response.status_code in [200, 201, 202],
                message_id=response.headers.get('X-Message-Id')
            )
        
        except Exception as e:
            logger.error(f"SendGrid template error: {str(e)}")
            return EmailResult(success=False, error=str(e))

