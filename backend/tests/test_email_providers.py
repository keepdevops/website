import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.email_interface import (
    EmailMessage,
    EmailResult,
    BulkEmailResult,
    EmailAttachment
)
from email_providers.templates import EmailTemplateManager


class MockEmailProvider:
    """Mock email provider for testing"""
    
    def __init__(self):
        self.sent_emails = []
        self.should_fail = False
    
    @property
    def provider_name(self) -> str:
        return "mock"
    
    def validate_config(self) -> bool:
        return True
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        if self.should_fail:
            return EmailResult(success=False, error="Mock failure")
        
        self.sent_emails.append(message)
        return EmailResult(success=True, message_id=f"mock_{len(self.sent_emails)}")
    
    async def send_bulk(self, messages):
        sent = 0
        for msg in messages:
            result = await self.send_email(msg)
            if result.success:
                sent += 1
        
        return BulkEmailResult(
            sent=sent,
            failed=len(messages) - sent,
            total=len(messages)
        )
    
    async def send_template(self, template_id, to, variables, from_email=None, tags=None):
        return EmailResult(success=True, message_id="mock_template")


@pytest.fixture
def email_message():
    """Create sample email message"""
    return EmailMessage(
        to=["test@example.com"],
        subject="Test Email",
        text_content="This is a test email",
        html_content="<p>This is a test email</p>"
    )


class TestEmailInterface:
    """Test email interface and data structures"""
    
    def test_email_message_creation(self):
        """Test creating email message"""
        msg = EmailMessage(
            to=["user@example.com"],
            subject="Hello",
            text_content="Test content",
            html_content="<p>Test content</p>",
            from_email="sender@example.com",
            tags=["test", "welcome"]
        )
        
        assert msg.to == ["user@example.com"]
        assert msg.subject == "Hello"
        assert len(msg.tags) == 2
    
    def test_email_result(self):
        """Test email result structure"""
        result = EmailResult(
            success=True,
            message_id="msg_123"
        )
        
        assert result.success is True
        assert result.message_id == "msg_123"


class TestEmailTemplateManager:
    """Test email template management"""
    
    def test_load_templates(self):
        """Test loading default templates"""
        manager = EmailTemplateManager()
        templates = manager.list_templates()
        
        assert "welcome" in templates
        assert "password_reset" in templates
        assert "subscription_created" in templates
    
    def test_render_welcome_template(self):
        """Test rendering welcome template"""
        manager = EmailTemplateManager()
        
        rendered = manager.render("welcome", {
            "name": "John",
            "app_name": "SaaS App",
            "login_url": "https://app.example.com/login"
        })
        
        assert "John" in rendered["text"]
        assert "SaaS App" in rendered["text"]
        assert "subject" in rendered
        assert "html" in rendered
    
    def test_render_password_reset_template(self):
        """Test rendering password reset template"""
        manager = EmailTemplateManager()
        
        rendered = manager.render("password_reset", {
            "name": "Jane",
            "app_name": "SaaS App",
            "reset_url": "https://app.example.com/reset/abc123"
        })
        
        assert "Jane" in rendered["text"]
        assert "reset/abc123" in rendered["text"]
    
    def test_add_custom_template(self):
        """Test adding custom template"""
        manager = EmailTemplateManager()
        
        manager.add_template(
            "custom",
            subject="Custom Subject",
            text="Hello ${name}",
            html="<h1>Hello ${name}</h1>"
        )
        
        assert "custom" in manager.list_templates()
        
        rendered = manager.render("custom", {"name": "Test"})
        assert "Test" in rendered["text"]
    
    def test_template_not_found(self):
        """Test rendering non-existent template"""
        manager = EmailTemplateManager()
        
        with pytest.raises(ValueError, match="Template not found"):
            manager.render("nonexistent", {})


class TestSendGridProvider:
    """Test SendGrid provider"""
    
    @pytest.mark.asyncio
    @patch('sendgrid.SendGridAPIClient')
    async def test_send_email_success(self, mock_client_class):
        """Test successful email send via SendGrid"""
        from email_providers.sendgrid import SendGridEmailProvider
        
        # Mock SendGrid response
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.headers = {"X-Message-Id": "msg_123"}
        
        mock_client = MagicMock()
        mock_client.send.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        provider = SendGridEmailProvider(api_key="test_key")
        
        message = EmailMessage(
            to=["test@example.com"],
            subject="Test",
            text_content="Test content"
        )
        
        result = await provider.send_email(message)
        
        assert result.success is True
        assert result.message_id == "msg_123"
    
    def test_provider_name(self):
        """Test SendGrid provider name"""
        from email_providers.sendgrid import SendGridEmailProvider
        
        with patch('sendgrid.SendGridAPIClient'):
            provider = SendGridEmailProvider(api_key="test_key")
            assert provider.provider_name == "sendgrid"


class TestMailgunProvider:
    """Test Mailgun provider"""
    
    @pytest.mark.asyncio
    async def test_send_email_success(self, email_message):
        """Test successful email send via Mailgun"""
        from email_providers.mailgun import MailgunEmailProvider
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "<msg_123>"}
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            provider = MailgunEmailProvider(
                api_key="test_key",
                domain="mg.example.com"
            )
            
            result = await provider.send_email(email_message)
            
            assert result.success is True
            assert result.message_id == "<msg_123>"
    
    def test_provider_name(self):
        """Test Mailgun provider name"""
        from email_providers.mailgun import MailgunEmailProvider
        
        provider = MailgunEmailProvider(api_key="test", domain="test.com")
        assert provider.provider_name == "mailgun"


class TestPostmarkProvider:
    """Test Postmark provider"""
    
    @pytest.mark.asyncio
    async def test_send_email_success(self, email_message):
        """Test successful email send via Postmark"""
        from email_providers.postmark import PostmarkEmailProvider
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"MessageID": "msg_123"}
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            provider = PostmarkEmailProvider(api_key="test_key")
            
            result = await provider.send_email(email_message)
            
            assert result.success is True
            assert result.message_id == "msg_123"
    
    def test_provider_name(self):
        """Test Postmark provider name"""
        from email_providers.postmark import PostmarkEmailProvider
        
        provider = PostmarkEmailProvider(api_key="test")
        assert provider.provider_name == "postmark"


class TestAWSSESProvider:
    """Test AWS SES provider"""
    
    @pytest.mark.asyncio
    @patch('boto3.client')
    async def test_send_email_success(self, mock_boto_client, email_message):
        """Test successful email send via AWS SES"""
        from email_providers.aws_ses import AWSSESEmailProvider
        
        mock_ses = MagicMock()
        mock_ses.send_raw_email.return_value = {"MessageId": "msg_123"}
        mock_boto_client.return_value = mock_ses
        
        provider = AWSSESEmailProvider(region="us-east-1")
        
        result = await provider.send_email(email_message)
        
        assert result.success is True
        assert result.message_id == "msg_123"
    
    def test_provider_name(self):
        """Test AWS SES provider name"""
        from email_providers.aws_ses import AWSSESEmailProvider
        
        with patch('boto3.client'):
            provider = AWSSESEmailProvider()
            assert provider.provider_name == "aws_ses"


class TestResendProvider:
    """Test Resend provider"""
    
    @pytest.mark.asyncio
    async def test_send_email_success(self, email_message):
        """Test successful email send via Resend"""
        from email_providers.resend import ResendEmailProvider
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "msg_123"}
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )
            
            provider = ResendEmailProvider(api_key="test_key")
            
            result = await provider.send_email(email_message)
            
            assert result.success is True
            assert result.message_id == "msg_123"
    
    def test_provider_name(self):
        """Test Resend provider name"""
        from email_providers.resend import ResendEmailProvider
        
        provider = ResendEmailProvider(api_key="test")
        assert provider.provider_name == "resend"


class TestEmailService:
    """Test high-level EmailService"""
    
    @pytest.mark.asyncio
    async def test_send_simple_email(self):
        """Test sending simple email"""
        from utils.email import EmailService
        
        provider = MockEmailProvider()
        service = EmailService(provider)
        
        result = await service.send_email(
            to_email="test@example.com",
            subject="Test",
            content="Test content"
        )
        
        assert result is True
        assert len(provider.sent_emails) == 1
    
    @pytest.mark.asyncio
    async def test_send_transactional_email(self):
        """Test sending transactional email with template"""
        from utils.email import EmailService
        
        provider = MockEmailProvider()
        service = EmailService(provider)
        
        result = await service.send_transactional_email(
            to_email="test@example.com",
            template_name="welcome",
            variables={"name": "John", "app_name": "Test App", "login_url": "https://test.com"}
        )
        
        assert result is True
        assert len(provider.sent_emails) == 1
        assert "John" in provider.sent_emails[0].text_content

