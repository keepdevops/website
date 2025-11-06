"""
Pusher Beams push notification provider implementation.
Real-time push notifications from the Pusher team.
"""
import httpx
from typing import Optional, List, Dict, Any
from core.push_notification_interface import PushNotificationInterface


class PusherBeamsPushProvider(PushNotificationInterface):
    """Pusher Beams push notification provider"""
    
    def __init__(self, instance_id: str, secret_key: str):
        self.instance_id = instance_id
        self.secret_key = secret_key
        self.base_url = f"https://{instance_id}.pushnotifications.pusher.com"
        self.headers = {
            "Authorization": f"Bearer {secret_key}",
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
        """Send push notification via Pusher Beams"""
        payload = {
            "interests": [f"user-{uid}" for uid in user_ids],
            "web": {
                "notification": {
                    "title": title,
                    "body": body,
                    "deep_link": action_url,
                    "icon": image_url
                }
            },
            "apns": {
                "aps": {
                    "alert": {
                        "title": title,
                        "body": body
                    }
                }
            },
            "fcm": {
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }
        
        if data:
            payload["web"]["data"] = data
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/publish_api/v1/instances/{self.instance_id}/publishes",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "notification_id": result.get("publishId"),
                "recipients": len(user_ids)
            }
    
    async def send_to_segment(
        self,
        segment: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send to interest (Pusher equivalent of segment)"""
        payload = {
            "interests": [segment],
            "web": {"notification": {"title": title, "body": body}},
            "apns": {"aps": {"alert": {"title": title, "body": body}}},
            "fcm": {"notification": {"title": title, "body": body}}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/publish_api/v1/instances/{self.instance_id}/publishes",
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
        """Device subscription handled client-side in Pusher Beams"""
        return True
    
    async def unsubscribe_device(self, device_token: str) -> bool:
        """Device unsubscription handled client-side"""
        return True
    
    async def get_notification_status(
        self,
        notification_id: str
    ) -> Dict[str, Any]:
        """Get notification status"""
        return {
            "notification_id": notification_id,
            "status": "published",
            "note": "Pusher Beams provides limited status tracking"
        }

