"""
OneSignal push notification provider implementation.
Popular push service with generous free tier and easy integration.
"""
import httpx
from typing import Optional, List, Dict, Any
from core.push_notification_interface import PushNotificationInterface


class OneSignalPushProvider(PushNotificationInterface):
    """OneSignal push notification provider"""
    
    def __init__(self, app_id: str, api_key: str):
        self.app_id = app_id
        self.api_key = api_key
        self.base_url = "https://onesignal.com/api/v1"
        self.headers = {
            "Authorization": f"Basic {api_key}",
            "Content-Type": "application/json"
        }
    
    async def send_notification(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image_url: Optional[str] = None,
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send push notification via OneSignal"""
        payload = {
            "app_id": self.app_id,
            "include_external_user_ids": user_ids,
            "headings": {"en": title},
            "contents": {"en": body}
        }
        
        if data:
            payload["data"] = data
        if image_url:
            payload["big_picture"] = image_url
        if action_url:
            payload["url"] = action_url
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/notifications",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "notification_id": result.get("id"),
                "recipients": result.get("recipients"),
                "errors": result.get("errors")
            }
    
    async def send_to_segment(
        self,
        segment: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send to user segment"""
        payload = {
            "app_id": self.app_id,
            "included_segments": [segment],
            "headings": {"en": title},
            "contents": {"en": body}
        }
        
        if data:
            payload["data"] = data
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/notifications",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def subscribe_device(
        self,
        user_id: str,
        device_token: str,
        platform: str
    ) -> bool:
        """Register device with OneSignal"""
        device_type = {"ios": 0, "android": 1, "web": 5}.get(platform, 1)
        
        payload = {
            "app_id": self.app_id,
            "device_type": device_type,
            "identifier": device_token,
            "external_user_id": user_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/players",
                json=payload,
                headers=self.headers
            )
            return response.status_code in [200, 201]
    
    async def unsubscribe_device(self, device_token: str) -> bool:
        """Unregister device - OneSignal manages this via player_id"""
        return True
    
    async def get_notification_status(
        self,
        notification_id: str
    ) -> Dict[str, Any]:
        """Get notification delivery status"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/notifications/{notification_id}?app_id={self.app_id}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "notification_id": notification_id,
                "successful": data.get("successful"),
                "failed": data.get("failed"),
                "converted": data.get("converted"),
                "remaining": data.get("remaining")
            }

