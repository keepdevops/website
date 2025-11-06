"""
Backblaze B2 storage provider implementation.
Cheapest storage option with S3-compatible API.
"""
from b2sdk.v2 import B2Api, InMemoryAccountInfo
from typing import Optional, List, Dict, Any
from datetime import datetime
from core.storage_interface import StorageProviderInterface


class BackblazeB2Provider(StorageProviderInterface):
    """Backblaze B2 storage provider"""
    
    def __init__(
        self,
        application_key_id: str,
        application_key: str,
        default_bucket: Optional[str] = None
    ):
        info = InMemoryAccountInfo()
        self.api = B2Api(info)
        self.api.authorize_account("production", application_key_id, application_key)
        self.default_bucket = default_bucket
    
    def _get_bucket(self, bucket_name: str):
        """Get bucket by name"""
        try:
            return self.api.get_bucket_by_name(bucket_name)
        except Exception as e:
            raise Exception(f"B2 bucket not found: {str(e)}")
    
    async def upload_file(
        self,
        bucket: str,
        path: str,
        file_data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Upload file to B2"""
        try:
            b2_bucket = self._get_bucket(bucket)
            
            file_info = metadata or {}
            
            uploaded_file = b2_bucket.upload_bytes(
                data_bytes=file_data,
                file_name=path,
                content_type=content_type or 'application/octet-stream',
                file_infos=file_info
            )
            
            # Get download URL
            download_url = self.api.get_download_url_for_file_name(bucket, path)
            
            return {
                "url": download_url,
                "path": path,
                "size": len(file_data)
            }
        except Exception as e:
            raise Exception(f"B2 upload failed: {str(e)}")
    
    async def download_file(self, bucket: str, path: str) -> bytes:
        """Download file from B2"""
        try:
            b2_bucket = self._get_bucket(bucket)
            downloaded = b2_bucket.download_file_by_name(path)
            
            # Read file content
            content = b2_bucket.download_file_by_name(path).save_to_bytes()
            return content
        except Exception as e:
            raise Exception(f"B2 download failed: {str(e)}")
    
    async def delete_file(self, bucket: str, path: str) -> bool:
        """Delete file from B2"""
        try:
            b2_bucket = self._get_bucket(bucket)
            
            # Get file version
            file_version = b2_bucket.get_file_info_by_name(path)
            self.api.delete_file_version(file_version.id_, path)
            
            return True
        except Exception as e:
            raise Exception(f"B2 delete failed: {str(e)}")
    
    async def get_public_url(
        self,
        bucket: str,
        path: str,
        expiration: Optional[int] = None
    ) -> str:
        """Get public URL (B2 doesn't support time-limited signed URLs in same way)"""
        try:
            download_url = self.api.get_download_url_for_file_name(bucket, path)
            return download_url
        except Exception as e:
            raise Exception(f"B2 URL generation failed: {str(e)}")
    
    async def list_files(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List files in B2 bucket"""
        try:
            b2_bucket = self._get_bucket(bucket)
            
            files = []
            for file_version, _ in b2_bucket.ls(
                folder_to_list=prefix or '',
                latest_only=True,
                recursive=True
            ):
                if len(files) >= limit:
                    break
                
                files.append({
                    'path': file_version.file_name,
                    'size': file_version.size,
                    'last_modified': datetime.fromtimestamp(
                        file_version.upload_timestamp / 1000
                    ).isoformat(),
                    'id': file_version.id_
                })
            
            return files
        except Exception as e:
            raise Exception(f"B2 list failed: {str(e)}")
    
    async def get_file_metadata(self, bucket: str, path: str) -> Dict[str, Any]:
        """Get file metadata from B2"""
        try:
            b2_bucket = self._get_bucket(bucket)
            file_info = b2_bucket.get_file_info_by_name(path)
            
            return {
                'size': file_info.size,
                'content_type': file_info.content_type,
                'last_modified': datetime.fromtimestamp(
                    file_info.upload_timestamp / 1000
                ).isoformat(),
                'id': file_info.id_,
                'metadata': file_info.file_info
            }
        except Exception as e:
            raise Exception(f"B2 metadata fetch failed: {str(e)}")
    
    async def create_bucket(
        self,
        name: str,
        public: bool = False,
        region: Optional[str] = None
    ) -> bool:
        """Create B2 bucket"""
        try:
            bucket_type = 'allPublic' if public else 'allPrivate'
            self.api.create_bucket(name, bucket_type)
            return True
        except Exception as e:
            raise Exception(f"B2 bucket creation failed: {str(e)}")
    
    async def delete_bucket(self, name: str) -> bool:
        """Delete B2 bucket"""
        try:
            b2_bucket = self._get_bucket(name)
            self.api.delete_bucket(b2_bucket)
            return True
        except Exception as e:
            raise Exception(f"B2 bucket deletion failed: {str(e)}")

