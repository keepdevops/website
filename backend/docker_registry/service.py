from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import httpx
from config import settings
from core.database import Database
from core.cache import Cache
from docker_registry.models import DockerImage, DownloadToken, DownloadRequest
from docker_registry.access_control import DockerAccessControl
import secrets
import logging

logger = logging.getLogger(__name__)

class DockerRegistryService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db
        self.cache = cache
        self.access_control = DockerAccessControl(db)
        self.registry_url = settings.docker_registry_url
        self.registry_token = settings.docker_registry_token
    
    async def generate_download_token(
        self,
        user_id: str,
        download_request: DownloadRequest
    ) -> DownloadToken:
        await self.access_control.validate_download_access(user_id, download_request.image_name)
        
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        token_data = {
            "user_id": user_id,
            "image_name": download_request.image_name,
            "tag": download_request.tag,
            "expires_at": expires_at.isoformat()
        }
        
        await self.cache.set_json(f"download_token:{token}", token_data, expiration=86400)
        
        download_url = f"{self.registry_url}/{download_request.image_name}:{download_request.tag}"
        
        return DownloadToken(
            token=token,
            image_name=download_request.image_name,
            expires_at=expires_at,
            download_url=download_url
        )
    
    async def verify_download_token(self, token: str) -> Optional[dict]:
        token_data = await self.cache.get_json(f"download_token:{token}")
        
        if not token_data:
            return None
        
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if datetime.utcnow() > expires_at:
            await self.cache.delete(f"download_token:{token}")
            return None
        
        return token_data
    
    async def get_available_images(self, user_id: str) -> List[DockerImage]:
        has_subscription = await self.access_control.check_user_access(user_id, "any")
        
        if not has_subscription:
            return []
        
        images = [
            DockerImage(
                id="1",
                name="saas-app",
                tag="latest",
                registry_url=self.registry_url,
                created_at=datetime.utcnow()
            )
        ]
        
        return images
    
    async def record_download(self, user_id: str, image_name: str, ip_address: Optional[str] = None):
        await self.access_control.log_download(user_id, image_name, ip_address)
    
    async def get_user_download_history(self, user_id: str, limit: int = 50):
        return await self.access_control.get_user_downloads(user_id, limit)

