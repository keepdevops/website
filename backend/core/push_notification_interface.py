"""
Abstract interface for push notification providers.
Defines operations for sending push notifications to users and devices.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class PushNotificationInterface(ABC):
    """Abstract interface for push notification providers"""
    
    @abstractmethod
    async def send_notification(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image_url: Optional[str] = None,
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send push notification to specific users.
        
        Args:
            user_ids: List of user identifiers
            title: Notification title
            body: Notification body text
            data: Optional custom data payload
            image_url: Optional image URL for rich notifications
            action_url: Optional deep link URL
            
        Returns:
            Dictionary with notification_id, recipients, etc.
        """
        pass
    
    @abstractmethod
    async def send_to_segment(
        self,
        segment: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send push notification to user segment.
        
        Args:
            segment: Segment name (e.g., 'premium_users', 'all')
            title: Notification title
            body: Notification body text
            data: Optional custom data payload
            
        Returns:
            Dictionary with notification_id, estimated recipients, etc.
        """
        pass
    
    @abstractmethod
    async def subscribe_device(
        self,
        user_id: str,
        device_token: str,
        platform: str
    ) -> bool:
        """
        Register device for push notifications.
        
        Args:
            user_id: User identifier
            device_token: Device push token
            platform: Platform type ('ios', 'android', 'web')
            
        Returns:
            True if subscription successful
        """
        pass
    
    @abstractmethod
    async def unsubscribe_device(
        self,
        device_token: str
    ) -> bool:
        """
        Unregister device from push notifications.
        
        Args:
            device_token: Device push token
            
        Returns:
            True if unsubscription successful
        """
        pass
    
    @abstractmethod
    async def get_notification_status(
        self,
        notification_id: str
    ) -> Dict[str, Any]:
        """
        Get delivery status of notification.
        
        Args:
            notification_id: Notification identifier
            
        Returns:
            Dictionary with status, delivered_count, etc.
        """
        pass

