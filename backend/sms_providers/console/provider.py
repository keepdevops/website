"""
Console SMS provider implementation.
Logs SMS messages to console for testing and development.
"""
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from core.sms_interface import SMSProviderInterface


class ConsoleSMSProvider(SMSProviderInterface):
    """Console/Mock SMS provider for testing"""
    
    def __init__(self):
        self.verification_codes: Dict[str, str] = {}
        self.messages: Dict[str, Dict] = {}
    
    async def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log SMS to console"""
        message_id = str(uuid.uuid4())
        
        print(f"\n{'='*50}")
        print(f"📱 SMS MESSAGE (Console Provider)")
        print(f"{'='*50}")
        print(f"To: {to}")
        print(f"From: {from_number or 'Console'}")
        print(f"Message: {message}")
        print(f"Message ID: {message_id}")
        print(f"{'='*50}\n")
        
        msg_data = {
            "message_id": message_id,
            "status": "delivered",
            "to": to,
            "from": from_number or "Console",
            "message": message,
            "cost": 0.0,
            "sent_at": datetime.utcnow().isoformat()
        }
        
        self.messages[message_id] = msg_data
        return msg_data
    
    async def send_verification_code(
        self,
        to: str,
        code: str,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send verification code to console"""
        message = template or f"Your verification code is: {code}"
        self.verification_codes[to] = code
        
        print(f"\n🔐 VERIFICATION CODE STORED")
        print(f"Phone: {to}")
        print(f"Code: {code}\n")
        
        return await self.send_sms(to, message)
    
    async def verify_phone(
        self,
        phone: str,
        code: str
    ) -> bool:
        """Verify phone number"""
        stored_code = self.verification_codes.get(phone)
        
        result = stored_code == code if stored_code else False
        
        print(f"\n✓ PHONE VERIFICATION")
        print(f"Phone: {phone}")
        print(f"Code: {code}")
        print(f"Result: {'✓ Success' if result else '✗ Failed'}\n")
        
        if result:
            del self.verification_codes[phone]
        
        return result
    
    async def get_message_status(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """Get message status"""
        if message_id in self.messages:
            return self.messages[message_id]
        
        return {
            "message_id": message_id,
            "status": "not_found"
        }

