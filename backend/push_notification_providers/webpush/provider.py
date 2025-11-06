"""
Web Push (VAPID) notification provider implementation.
Native browser push notifications using Web Push protocol.
"""
from pywebpush import webpush, WebPushException
from typing import Optional, List, Dict, Any
import json
from core.push_notification_interface import PushNotificationInterface


class WebPushProvider(PushNotificationInterface):
    """Web Push (VAPID) notification provider"""
    
    def __init__(
        self,
        vapid_public_key: str,
        vapid_private_key: str,
        vapid_subject: str = "mailto:admin@yourapp.com"
    ):
        self.vapid_public_key = vapid_public_key
        self.vapid_private_key = vapid_private_key
        self.vapid_subject = vapid_subject
        self.subscriptions: Dict[str, List[Dict]] = {}  # user_id -> [subscription_info]
    
    async def send_notification(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image_url: Optional[str] = None,
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send web push notification"""
        payload = {
            "title": title,
            "body": body,
            "icon": image_url,
            "url": action_url,
            "data": data or {}
        }
        
        sent_count = 0
        failed_count = 0
        
        for user_id in user_ids:
            subscriptions = self.subscriptions.get(user_id, [])
            
            for subscription in subscriptions:
                try:
                    webpush(
                        subscription_info=subscription,
                        data=json.dumps(payload),
                        vapid_private_key=self.vapid_private_key,
                        vapid_claims={
                            "sub": self.vapid_subject
                        }
                    )
                    sent_count += 1
                except WebPushException:
                    failed_count += 1
        
        return {
            "notification_id": "webpush",
            "recipients": sent_count,
            "failures": failed_count
        }
    
    async def send_to_segment(
        self,
        segment: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send to all subscribed users (segment not directly supported)"""
        all_user_ids = list(self.subscriptions.keys())
        return await self.send_notification(all_user_ids, title, body, data)
    
    async def subscribe_device(
        self,
        user_id: str,
        device_token: str,
        platform: str
    ) -> bool:
        """Register web push subscription"""
        try:
            subscription_info = json.loads(device_token)
            
            if user_id not in self.subscriptions:
                self.subscriptions[user_id] = []
            
            self.subscriptions[user_id].append(subscription_info)
            return True
        except Exception:
            return False
    
    async def unsubscribe_device(self, device_token: str) -> bool:
        """Unregister web push subscription"""
        for user_id in self.subscriptions:
            self.subscriptions[user_id] = [
                sub for sub in self.subscriptions[user_id]
                if json.dumps(sub) != device_token
            ]
        return True
    
    async def get_notification_status(
        self,
        notification_id: str
    ) -> Dict[str, Any]:
        """Web Push doesn't provide delivery tracking"""
        return {
            "notification_id": notification_id,
            "status": "sent",
            "note": "Web Push does not provide delivery tracking"
        }

