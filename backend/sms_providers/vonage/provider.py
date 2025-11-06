"""
Vonage (formerly Nexmo) SMS provider implementation.
Global SMS delivery with competitive pricing.
"""
import httpx
from typing import Optional, Dict, Any
from datetime import datetime
from core.sms_interface import SMSProviderInterface


class VonageSMSProvider(SMSProviderInterface):
    """Vonage/Nexmo SMS provider"""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        from_number: Optional[str] = None
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.from_number = from_number or "Vonage"
        self.base_url = "https://rest.nexmo.com"
        self.verification_codes: Dict[str, str] = {}
    
    async def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS via Vonage"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sms/json",
                json={
                    "from": from_number or self.from_number,
                    "to": to,
                    "text": message,
                    "api_key": self.api_key,
                    "api_secret": self.api_secret
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("messages"):
                msg = data["messages"][0]
                
                return {
                    "message_id": msg.get("message-id"),
                    "status": msg.get("status"),
                    "to": to,
                    "from": from_number or self.from_number,
                    "cost": msg.get("message-price"),
                    "sent_at": datetime.utcnow().isoformat()
                }
            
            raise Exception(f"Vonage SMS send failed: {data}")
    
    async def send_verification_code(
        self,
        to: str,
        code: str,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send verification code"""
        message = template or f"Your verification code is: {code}"
        self.verification_codes[to] = code
        return await self.send_sms(to, message)
    
    async def verify_phone(
        self,
        phone: str,
        code: str
    ) -> bool:
        """Verify phone number"""
        stored_code = self.verification_codes.get(phone)
        
        if stored_code and stored_code == code:
            del self.verification_codes[phone]
            return True
        
        return False
    
    async def get_message_status(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """Get message status"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/search/message",
                params={
                    "api_key": self.api_key,
                    "api_secret": self.api_secret,
                    "id": message_id
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "message_id": message_id,
                "status": data.get("status"),
                "to": data.get("to"),
                "from": data.get("from"),
                "sent_at": data.get("date-sent"),
                "delivered_at": data.get("date-received")
            }

