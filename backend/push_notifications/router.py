"""
Push notification API router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel

from push_notifications.service import PushNotificationService
from core.push_notification_factory import get_push_notification_provider
from core.dependencies import get_current_user_id


router = APIRouter(prefix="/push", tags=["push-notifications"])


def get_push_service() -> PushNotificationService:
    """Get configured push notification service"""
    provider = get_push_notification_provider()
    return PushNotificationService(provider=provider)


class SendNotificationRequest(BaseModel):
    """Send notification request"""
    user_id: str
    title: str
    message: str
    action_url: Optional[str] = None
    data: Optional[dict] = None


class BroadcastRequest(BaseModel):
    """Broadcast notification request"""
    title: str
    message: str
    action_url: Optional[str] = None


class RegisterDeviceRequest(BaseModel):
    """Register device request"""
    device_token: str
    platform: str  # 'ios', 'android', 'web'


@router.post("/send")
async def send_notification(
    request: SendNotificationRequest,
    admin_user: str = Depends(get_current_user_id),
    push_service: PushNotificationService = Depends(get_push_service)
):
    """Send push notification to user (admin only)"""
    try:
        result = await push_service.notify_user(
            user_id=request.user_id,
            title=request.title,
            message=request.message,
            action_url=request.action_url,
            data=request.data
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )


@router.post("/broadcast")
async def broadcast_notification(
    request: BroadcastRequest,
    admin_user: str = Depends(get_current_user_id),
    push_service: PushNotificationService = Depends(get_push_service)
):
    """Broadcast notification to all users (admin only)"""
    try:
        result = await push_service.broadcast_to_all(
            title=request.title,
            message=request.message,
            action_url=request.action_url
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to broadcast notification: {str(e)}"
        )


@router.post("/register-device")
async def register_device(
    request: RegisterDeviceRequest,
    user_id: str = Depends(get_current_user_id),
    push_service: PushNotificationService = Depends(get_push_service)
):
    """Register device for push notifications"""
    try:
        success = await push_service.register_device(
            user_id=user_id,
            device_token=request.device_token,
            platform=request.platform
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register device: {str(e)}"
        )


@router.delete("/unregister-device/{device_token}")
async def unregister_device(
    device_token: str,
    user_id: str = Depends(get_current_user_id),
    push_service: PushNotificationService = Depends(get_push_service)
):
    """Unregister device from push notifications"""
    try:
        success = await push_service.unregister_device(device_token)
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unregister device: {str(e)}"
        )

