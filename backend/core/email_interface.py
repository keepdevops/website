from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class EmailPriority(Enum):
    """Email priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class EmailAttachment:
    """Email attachment"""
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"


@dataclass
class EmailMessage:
    """Email message structure"""
    to: List[str]
    subject: str
    text_content: str
    html_content: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    reply_to: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    attachments: Optional[List[EmailAttachment]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    priority: EmailPriority = EmailPriority.NORMAL


@dataclass
class EmailResult:
    """Result of email send operation"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None


@dataclass
class BulkEmailResult:
    """Result of bulk email send operation"""
    sent: int
    failed: int
    total: int
    errors: List[str] = field(default_factory=list)


class EmailProviderInterface(ABC):
    """Abstract interface for email providers (SendGrid, Mailgun, etc.)"""
    
    @abstractmethod
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """
        Send a single email.
        
        Args:
            message: Email message to send
        
        Returns:
            EmailResult with success status and message ID
        """
        pass
    
    @abstractmethod
    async def send_bulk(self, messages: List[EmailMessage]) -> BulkEmailResult:
        """
        Send multiple emails in batch.
        
        Args:
            messages: List of email messages
        
        Returns:
            BulkEmailResult with counts and errors
        """
        pass
    
    @abstractmethod
    async def send_template(
        self,
        template_id: str,
        to: List[str],
        variables: Dict[str, Any],
        from_email: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> EmailResult:
        """
        Send email using provider's template system.
        
        Args:
            template_id: Provider template ID
            to: List of recipient emails
            variables: Template variables
            from_email: Optional sender email
            tags: Optional tags for tracking
        
        Returns:
            EmailResult with success status
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this email provider"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate provider configuration (API keys, domains, etc.)
        
        Returns:
            True if config is valid, False otherwise
        """
        pass

