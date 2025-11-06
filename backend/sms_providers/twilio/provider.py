"""
Twilio SMS provider implementation.
Industry-leading SMS platform with global coverage.
"""
from twilio.rest import Client
from typing import Optional, Dict, Any
from datetime import datetime
from core.sms_interface import SMSProviderInterface


class TwilioSMSProvider(SMSProviderInterface):
    """Twilio SMS provider"""
    
    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_number: Optional[str] = None
    ):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
        self.verification_codes: Dict[str, str] = {}  # In-memory storage for demo
    
    async def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            msg = self.client.messages.create(
                body=message,
                from_=from_number or self.from_number,
                to=to
            )
            
            return {
                "message_id": msg.sid,
                "status": msg.status,
                "to": to,
                "from": msg.from_,
                "cost": msg.price,
                "sent_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise Exception(f"Twilio SMS send failed: {str(e)}")
    
    async def send_verification_code(
        self,
        to: str,
        code: str,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send verification code via SMS"""
        message = template or f"Your verification code is: {code}"
        
        # Store code for verification
        self.verification_codes[to] = code
        
        return await self.send_sms(to, message)
    
    async def verify_phone(
        self,
        phone: str,
        code: str
    ) -> bool:
        """Verify phone number with code"""
        stored_code = self.verification_codes.get(phone)
        
        if stored_code and stored_code == code:
            # Remove used code
            del self.verification_codes[phone]
            return True
        
        return False
    
    async def get_message_status(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """Get message status from Twilio"""
        try:
            msg = self.client.messages(message_id).fetch()
            
            return {
                "message_id": msg.sid,
                "status": msg.status,
                "error_code": msg.error_code,
                "error_message": msg.error_message,
                "to": msg.to,
                "from": msg.from_,
                "sent_at": msg.date_sent.isoformat() if msg.date_sent else None,
                "delivered_at": msg.date_updated.isoformat() if msg.date_updated else None
            }
        except Exception as e:
            raise Exception(f"Twilio status fetch failed: {str(e)}")

