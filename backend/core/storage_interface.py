"""
Abstract interface for cloud storage providers.
Defines common operations for file upload, download, and management.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime


class StorageProviderInterface(ABC):
    """Abstract interface for cloud storage providers"""
    
    @abstractmethod
    async def upload_file(
        self,
        bucket: str,
        path: str,
        file_data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to storage.
        
        Args:
            bucket: Target bucket/container name
            path: File path within bucket
            file_data: File content as bytes
            content_type: MIME type (e.g., 'image/jpeg')
            metadata: Optional key-value metadata
            
        Returns:
            Dictionary with 'url', 'path', and 'size'
        """
        pass
    
    @abstractmethod
    async def download_file(
        self,
        bucket: str,
        path: str
    ) -> bytes:
        """
        Download file as bytes.
        
        Args:
            bucket: Source bucket/container name
            path: File path within bucket
            
        Returns:
            File content as bytes
        """
        pass
    
    @abstractmethod
    async def delete_file(
        self,
        bucket: str,
        path: str
    ) -> bool:
        """
        Delete a file.
        
        Args:
            bucket: Target bucket/container name
            path: File path within bucket
            
        Returns:
            True if deleted successfully
        """
        pass
    
    @abstractmethod
    async def get_public_url(
        self,
        bucket: str,
        path: str,
        expiration: Optional[int] = None
    ) -> str:
        """
        Get public URL or signed URL with expiration.
        
        Args:
            bucket: Bucket/container name
            path: File path within bucket
            expiration: Optional expiration in seconds (for signed URLs)
            
        Returns:
            Public or signed URL string
        """
        pass
    
    @abstractmethod
    async def list_files(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List files in bucket with optional prefix filter.
        
        Args:
            bucket: Bucket/container name
            prefix: Optional prefix filter
            limit: Maximum number of files to return
            
        Returns:
            List of file metadata dictionaries
        """
        pass
    
    @abstractmethod
    async def get_file_metadata(
        self,
        bucket: str,
        path: str
    ) -> Dict[str, Any]:
        """
        Get file metadata.
        
        Args:
            bucket: Bucket/container name
            path: File path within bucket
            
        Returns:
            Dictionary with size, content_type, last_modified, etc.
        """
        pass
    
    @abstractmethod
    async def create_bucket(
        self,
        name: str,
        public: bool = False,
        region: Optional[str] = None
    ) -> bool:
        """
        Create a new bucket/container.
        
        Args:
            name: Bucket/container name
            public: Whether bucket should be publicly accessible
            region: Optional region/location
            
        Returns:
            True if created successfully
        """
        pass
    
    @abstractmethod
    async def delete_bucket(
        self,
        name: str
    ) -> bool:
        """
        Delete a bucket (must be empty).
        
        Args:
            name: Bucket/container name
            
        Returns:
            True if deleted successfully
        """
        pass

