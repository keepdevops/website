"""
Push notification service providing high-level operations.
"""
from typing import Optional, Dict, Any, List
from core.push_notification_interface import PushNotificationInterface


class PushNotificationService:
    """High-level push notification service"""
    
    def __init__(self, provider: PushNotificationInterface):
        self.provider = provider
    
    async def notify_user(
        self,
        user_id: str,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send notification to single user.
        
        Args:
            user_id: User identifier
            title: Notification title
            message: Notification message
            action_url: Optional action URL
            data: Optional custom data
            
        Returns:
            Notification result
        """
        return await self.provider.send_notification(
            user_ids=[user_id],
            title=title,
            body=message,
            action_url=action_url,
            data=data
        )
    
    async def notify_users(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send notification to multiple users"""
        return await self.provider.send_notification(
            user_ids=user_ids,
            title=title,
            body=message,
            action_url=action_url
        )
    
    async def broadcast_to_all(
        self,
        title: str,
        message: str,
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Broadcast notification to all users"""
        return await self.provider.send_to_segment(
            segment="all",
            title=title,
            body=message
        )
    
    async def notify_segment(
        self,
        segment: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send notification to user segment"""
        return await self.provider.send_to_segment(
            segment=segment,
            title=title,
            body=message,
            data=data
        )
    
    async def register_device(
        self,
        user_id: str,
        device_token: str,
        platform: str
    ) -> bool:
        """Register user device for push notifications"""
        return await self.provider.subscribe_device(
            user_id=user_id,
            device_token=device_token,
            platform=platform
        )
    
    async def unregister_device(self, device_token: str) -> bool:
        """Unregister device from push notifications"""
        return await self.provider.unsubscribe_device(device_token)
    
    async def get_status(self, notification_id: str) -> Dict[str, Any]:
        """Get notification delivery status"""
        return await self.provider.get_notification_status(notification_id)

