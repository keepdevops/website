"""
Abstract interface for SMS/phone providers.
Defines operations for sending SMS messages and verifying phone numbers.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime


class SMSProviderInterface(ABC):
    """Abstract interface for SMS providers"""
    
    @abstractmethod
    async def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send SMS message.
        
        Args:
            to: Recipient phone number (E.164 format)
            message: Message text
            from_number: Sender phone number (optional)
            
        Returns:
            Dictionary with message_id, status, cost, etc.
        """
        pass
    
    @abstractmethod
    async def send_verification_code(
        self,
        to: str,
        code: str,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send verification code via SMS.
        
        Args:
            to: Recipient phone number
            code: Verification code
            template: Optional message template
            
        Returns:
            Dictionary with message_id and status
        """
        pass
    
    @abstractmethod
    async def verify_phone(
        self,
        phone: str,
        code: str
    ) -> bool:
        """
        Verify phone number with code.
        
        Args:
            phone: Phone number to verify
            code: Verification code
            
        Returns:
            True if verification successful
        """
        pass
    
    @abstractmethod
    async def get_message_status(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """
        Get status of sent message.
        
        Args:
            message_id: Message identifier
            
        Returns:
            Dictionary with status, delivery info, etc.
        """
        pass

