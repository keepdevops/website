"""
Firebase Cloud Messaging (FCM) push notification provider.
Google's push notification solution with global reach.
"""
from firebase_admin import credentials, initialize_app, messaging
from typing import Optional, List, Dict, Any
from core.push_notification_interface import PushNotificationInterface


class FirebasePushProvider(PushNotificationInterface):
    """Firebase Cloud Messaging push provider"""
    
    def __init__(
        self,
        credentials_path: str,
        project_id: Optional[str] = None
    ):
        cred = credentials.Certificate(credentials_path)
        try:
            initialize_app(cred, {'projectId': project_id} if project_id else None)
        except ValueError:
            # App already initialized
            pass
        
        self.device_tokens: Dict[str, List[str]] = {}  # user_id -> [tokens]
    
    async def send_notification(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image_url: Optional[str] = None,
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send push notification via FCM"""
        tokens = []
        for user_id in user_ids:
            tokens.extend(self.device_tokens.get(user_id, []))
        
        if not tokens:
            return {"notification_id": None, "recipients": 0, "error": "No device tokens"}
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image_url
            ),
            data=data or {},
            tokens=tokens
        )
        
        response = messaging.send_multicast(message)
        
        return {
            "notification_id": "fcm_multicast",
            "recipients": response.success_count,
            "failures": response.failure_count
        }
    
    async def send_to_segment(
        self,
        segment: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send to topic (FCM equivalent of segment)"""
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data or {},
            topic=segment
        )
        
        message_id = messaging.send(message)
        
        return {
            "notification_id": message_id,
            "topic": segment
        }
    
    async def subscribe_device(
        self,
        user_id: str,
        device_token: str,
        platform: str
    ) -> bool:
        """Register device token"""
        if user_id not in self.device_tokens:
            self.device_tokens[user_id] = []
        
        if device_token not in self.device_tokens[user_id]:
            self.device_tokens[user_id].append(device_token)
        
        return True
    
    async def unsubscribe_device(self, device_token: str) -> bool:
        """Unregister device token"""
        for user_id in self.device_tokens:
            if device_token in self.device_tokens[user_id]:
                self.device_tokens[user_id].remove(device_token)
        
        return True
    
    async def get_notification_status(
        self,
        notification_id: str
    ) -> Dict[str, Any]:
        """FCM doesn't provide detailed status tracking"""
        return {
            "notification_id": notification_id,
            "status": "sent",
            "note": "FCM does not provide detailed delivery tracking"
        }

