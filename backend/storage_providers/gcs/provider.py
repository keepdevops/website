"""
Google Cloud Storage provider implementation.
Full-featured with multi-region support and Cloud CDN integration.
"""
from google.cloud import storage
from google.oauth2 import service_account
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from core.storage_interface import StorageProviderInterface


class GoogleCloudStorageProvider(StorageProviderInterface):
    """Google Cloud Storage provider"""
    
    def __init__(
        self,
        project_id: str,
        credentials_path: Optional[str] = None,
        default_bucket: Optional[str] = None
    ):
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = storage.Client(
                project=project_id,
                credentials=credentials
            )
        else:
            # Use default credentials (from environment)
            self.client = storage.Client(project=project_id)
        
        self.project_id = project_id
        self.default_bucket = default_bucket
    
    async def upload_file(
        self,
        bucket: str,
        path: str,
        file_data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Upload file to GCS"""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(path)
            
            if content_type:
                blob.content_type = content_type
            if metadata:
                blob.metadata = metadata
            
            blob.upload_from_string(file_data)
            
            # Get public URL
            url = blob.public_url
            
            return {
                "url": url,
                "path": path,
                "size": len(file_data)
            }
        except Exception as e:
            raise Exception(f"GCS upload failed: {str(e)}")
    
    async def download_file(self, bucket: str, path: str) -> bytes:
        """Download file from GCS"""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(path)
            return blob.download_as_bytes()
        except Exception as e:
            raise Exception(f"GCS download failed: {str(e)}")
    
    async def delete_file(self, bucket: str, path: str) -> bool:
        """Delete file from GCS"""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(path)
            blob.delete()
            return True
        except Exception as e:
            raise Exception(f"GCS delete failed: {str(e)}")
    
    async def get_public_url(
        self,
        bucket: str,
        path: str,
        expiration: Optional[int] = None
    ) -> str:
        """Get public or signed URL"""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(path)
            
            if expiration:
                # Generate signed URL
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=timedelta(seconds=expiration),
                    method="GET"
                )
                return url
            else:
                # Return public URL
                return blob.public_url
        except Exception as e:
            raise Exception(f"GCS URL generation failed: {str(e)}")
    
    async def list_files(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List files in GCS bucket"""
        try:
            bucket_obj = self.client.bucket(bucket)
            blobs = bucket_obj.list_blobs(prefix=prefix, max_results=limit)
            
            files = []
            for blob in blobs:
                files.append({
                    'path': blob.name,
                    'size': blob.size,
                    'last_modified': blob.updated.isoformat() if blob.updated else '',
                    'content_type': blob.content_type,
                    'etag': blob.etag
                })
            
            return files
        except Exception as e:
            raise Exception(f"GCS list failed: {str(e)}")
    
    async def get_file_metadata(self, bucket: str, path: str) -> Dict[str, Any]:
        """Get file metadata from GCS"""
        try:
            bucket_obj = self.client.bucket(bucket)
            blob = bucket_obj.blob(path)
            blob.reload()  # Fetch latest metadata
            
            return {
                'size': blob.size,
                'content_type': blob.content_type,
                'last_modified': blob.updated.isoformat() if blob.updated else '',
                'etag': blob.etag,
                'metadata': blob.metadata or {}
            }
        except Exception as e:
            raise Exception(f"GCS metadata fetch failed: {str(e)}")
    
    async def create_bucket(
        self,
        name: str,
        public: bool = False,
        region: Optional[str] = None
    ) -> bool:
        """Create GCS bucket"""
        try:
            bucket = self.client.bucket(name)
            
            if region:
                bucket.location = region
            
            bucket = self.client.create_bucket(bucket)
            
            if public:
                # Make bucket publicly readable
                bucket.make_public(recursive=True, future=True)
            
            return True
        except Exception as e:
            raise Exception(f"GCS bucket creation failed: {str(e)}")
    
    async def delete_bucket(self, name: str) -> bool:
        """Delete GCS bucket"""
        try:
            bucket = self.client.bucket(name)
            bucket.delete()
            return True
        except Exception as e:
            raise Exception(f"GCS bucket deletion failed: {str(e)}")

