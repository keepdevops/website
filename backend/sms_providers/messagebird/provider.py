"""
MessageBird SMS provider implementation.
European-focused SMS platform with global reach.
"""
import httpx
from typing import Optional, Dict, Any
from datetime import datetime
from core.sms_interface import SMSProviderInterface


class MessageBirdSMSProvider(SMSProviderInterface):
    """MessageBird SMS provider"""
    
    def __init__(
        self,
        api_key: str,
        from_number: Optional[str] = None
    ):
        self.api_key = api_key
        self.from_number = from_number or "MessageBird"
        self.base_url = "https://rest.messagebird.com"
        self.verification_codes: Dict[str, str] = {}
    
    async def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS via MessageBird"""
        headers = {"Authorization": f"AccessKey {self.api_key}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json={
                    "originator": from_number or self.from_number,
                    "recipients": [to],
                    "body": message
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "message_id": data.get("id"),
                "status": data.get("status"),
                "to": to,
                "from": data.get("originator"),
                "cost": data.get("pricing", {}).get("amount"),
                "sent_at": data.get("createdDatetime")
            }
    
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
        headers = {"Authorization": f"AccessKey {self.api_key}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/messages/{message_id}",
                headers=headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "message_id": message_id,
                "status": data.get("status"),
                "to": data.get("recipients", {}).get("totalDeliveredCount"),
                "sent_at": data.get("createdDatetime"),
                "delivered_at": data.get("receivedDatetime")
            }

