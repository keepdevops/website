"""
High-level storage service providing common file operations.
Abstracts provider-specific details for application use.
"""
from typing import Optional, Dict, Any, List
import hashlib
import uuid
from datetime import datetime
from core.storage_interface import StorageProviderInterface


class StorageService:
    """High-level storage service with common operations"""
    
    def __init__(self, provider: StorageProviderInterface, default_bucket: str):
        self.provider = provider
        self.default_bucket = default_bucket
    
    async def upload_user_avatar(
        self,
        user_id: str,
        file_data: bytes,
        filename: str
    ) -> str:
        """
        Upload user avatar image.
        
        Args:
            user_id: User identifier
            file_data: Image file bytes
            filename: Original filename
            
        Returns:
            Public URL of uploaded avatar
        """
        # Generate unique path
        file_ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'jpg'
        path = f"avatars/{user_id}/avatar.{file_ext}"
        
        result = await self.provider.upload_file(
            bucket=self.default_bucket,
            path=path,
            file_data=file_data,
            content_type=f"image/{file_ext}"
        )
        
        return result["url"]
    
    async def upload_document(
        self,
        user_id: str,
        file_data: bytes,
        filename: str,
        folder: str = "documents"
    ) -> Dict[str, Any]:
        """
        Upload a document file.
        
        Args:
            user_id: User identifier
            file_data: File bytes
            filename: Original filename
            folder: Storage folder/prefix
            
        Returns:
            Dictionary with url, path, and size
        """
        # Generate unique filename to avoid collisions
        unique_id = str(uuid.uuid4())[:8]
        file_ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'bin'
        safe_filename = filename.rsplit('.', 1)[0].replace(' ', '_')[:50]
        path = f"{folder}/{user_id}/{unique_id}_{safe_filename}.{file_ext}"
        
        result = await self.provider.upload_file(
            bucket=self.default_bucket,
            path=path,
            file_data=file_data,
            metadata={
                'user_id': user_id,
                'original_filename': filename,
                'uploaded_at': datetime.utcnow().isoformat()
            }
        )
        
        return result
    
    async def upload_file(
        self,
        path: str,
        file_data: bytes,
        content_type: Optional[str] = None,
        bucket: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generic file upload"""
        return await self.provider.upload_file(
            bucket=bucket or self.default_bucket,
            path=path,
            file_data=file_data,
            content_type=content_type
        )
    
    async def download_file(
        self,
        path: str,
        bucket: Optional[str] = None
    ) -> bytes:
        """Download file by path"""
        return await self.provider.download_file(
            bucket=bucket or self.default_bucket,
            path=path
        )
    
    async def delete_file(
        self,
        path: str,
        bucket: Optional[str] = None
    ) -> bool:
        """Delete file by path"""
        return await self.provider.delete_file(
            bucket=bucket or self.default_bucket,
            path=path
        )
    
    async def get_public_url(
        self,
        path: str,
        expiration: Optional[int] = None,
        bucket: Optional[str] = None
    ) -> str:
        """Get public or signed URL"""
        return await self.provider.get_public_url(
            bucket=bucket or self.default_bucket,
            path=path,
            expiration=expiration
        )
    
    async def list_user_files(
        self,
        user_id: str,
        folder: str = "documents",
        bucket: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all files for a specific user"""
        prefix = f"{folder}/{user_id}/"
        
        return await self.provider.list_files(
            bucket=bucket or self.default_bucket,
            prefix=prefix
        )

