from typing import List, Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from core.email_interface import (
    EmailProviderInterface,
    EmailMessage,
    EmailResult,
    BulkEmailResult
)
import logging

logger = logging.getLogger(__name__)


class AWSSESEmailProvider(EmailProviderInterface):
    """AWS SES (Simple Email Service) provider implementation"""
    
    def __init__(
        self,
        region: str = "us-east-1",
        default_from_email: str = "noreply@yoursaas.com",
        configuration_set: Optional[str] = None
    ):
        self.region = region
        self.default_from_email = default_from_email
        self.configuration_set = configuration_set
        self.client = boto3.client('ses', region_name=region)
    
    @property
    def provider_name(self) -> str:
        return "aws_ses"
    
    def validate_config(self) -> bool:
        """Validate AWS SES configuration"""
        try:
            # Test by getting send quota
            self.client.get_send_quota()
            logger.info("AWS SES configuration is valid")
            return True
        except ClientError as e:
            logger.error(f"AWS SES config validation failed: {str(e)}")
            return False
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """Send email via AWS SES"""
        try:
            # Build email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = message.from_email or self.default_from_email
            msg['To'] = ", ".join(message.to)
            
            if message.reply_to:
                msg['Reply-To'] = message.reply_to
            
            if message.cc:
                msg['Cc'] = ", ".join(message.cc)
            
            # Add text and HTML parts
            text_part = MIMEText(message.text_content, 'plain')
            msg.attach(text_part)
            
            if message.html_content:
                html_part = MIMEText(message.html_content, 'html')
                msg.attach(html_part)
            
            # Add attachments
            if message.attachments:
                for attachment in message.attachments:
                    part = MIMEApplication(attachment.content)
                    part.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=attachment.filename
                    )
                    msg.attach(part)
            
            # Send via SES
            destinations = message.to[:]
            if message.cc:
                destinations.extend(message.cc)
            if message.bcc:
                destinations.extend(message.bcc)
            
            send_args = {
                'Source': message.from_email or self.default_from_email,
                'Destinations': destinations,
                'RawMessage': {'Data': msg.as_string()}
            }
            
            if self.configuration_set:
                send_args['ConfigurationSetName'] = self.configuration_set
            
            response = self.client.send_raw_email(**send_args)
            
            logger.info(f"AWS SES email sent to {message.to}, ID: {response['MessageId']}")
            
            return EmailResult(
                success=True,
                message_id=response['MessageId'],
                provider_response=response
            )
        
        except ClientError as e:
            logger.error(f"AWS SES error: {str(e)}")
            return EmailResult(success=False, error=str(e))
        except Exception as e:
            logger.error(f"AWS SES unexpected error: {str(e)}")
            return EmailResult(success=False, error=str(e))
    
    async def send_bulk(self, messages: List[EmailMessage]) -> BulkEmailResult:
        """Send multiple emails via AWS SES"""
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
        """Send email using AWS SES template"""
        try:
            send_args = {
                'Source': from_email or self.default_from_email,
                'Destination': {'ToAddresses': to},
                'Template': template_id,
                'TemplateData': str(variables)  # JSON string
            }
            
            if self.configuration_set:
                send_args['ConfigurationSetName'] = self.configuration_set
            
            response = self.client.send_templated_email(**send_args)
            
            return EmailResult(
                success=True,
                message_id=response['MessageId']
            )
        
        except ClientError as e:
            logger.error(f"AWS SES template error: {str(e)}")
            return EmailResult(success=False, error=str(e))

