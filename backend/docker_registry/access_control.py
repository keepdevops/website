from typing import Optional
from fastapi import HTTPException, status
from core.database import Database
import logging

logger = logging.getLogger(__name__)

class DockerAccessControl:
    def __init__(self, db: Database):
        self.db = db
    
    async def check_user_access(self, user_id: str, image_name: str) -> bool:
        subscription = await self._get_active_subscription(user_id)
        
        if not subscription:
            logger.warning(f"No active subscription for user: {user_id}")
            return False
        
        if subscription.get("status") not in ["active", "trialing"]:
            logger.warning(f"Inactive subscription for user: {user_id}")
            return False
        
        product_access = await self._check_product_access(subscription, image_name)
        
        return product_access
    
    async def _get_active_subscription(self, user_id: str) -> Optional[dict]:
        result = await self.db.get_all("subscriptions", {"user_id": user_id}, limit=1)
        return result.data[0] if result.data else None
    
    async def _check_product_access(self, subscription: dict, image_name: str) -> bool:
        return True
    
    async def validate_download_access(self, user_id: str, image_name: str):
        has_access = await self.check_user_access(user_id, image_name)
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Active subscription required."
            )
        
        return True
    
    async def log_download(self, user_id: str, image_name: str, ip_address: Optional[str] = None):
        try:
            await self.db.create("download_logs", {
                "user_id": user_id,
                "image_name": image_name,
                "ip_address": ip_address
            })
        except Exception as e:
            logger.error(f"Error logging download: {str(e)}")
    
    async def get_user_downloads(self, user_id: str, limit: int = 50):
        result = await self.db.get_all("download_logs", {"user_id": user_id}, limit=limit)
        return result.data or []
    
    async def revoke_access(self, user_id: str):
        logger.info(f"Revoking download access for user: {user_id}")
        return True

