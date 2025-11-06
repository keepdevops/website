"""
Supabase Storage provider implementation.
Integrated with Supabase Auth and Row Level Security.
"""
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime
from core.storage_interface import StorageProviderInterface


class SupabaseStorageProvider(StorageProviderInterface):
    """Supabase Storage provider with RLS integration"""
    
    def __init__(
        self,
        url: str,
        key: str,
        default_bucket: Optional[str] = None
    ):
        self.client: Client = create_client(url, key)
        self.default_bucket = default_bucket
        self.base_url = url
    
    async def upload_file(
        self,
        bucket: str,
        path: str,
        file_data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Upload file to Supabase Storage"""
        try:
            options = {}
            if content_type:
                options['content-type'] = content_type
            if metadata:
                options['x-upsert'] = 'true'  # Allow overwriting
            
            result = self.client.storage.from_(bucket).upload(
                path=path,
                file=file_data,
                file_options=options
            )
            
            # Get public URL
            public_url = self.client.storage.from_(bucket).get_public_url(path)
            
            return {
                "url": public_url,
                "path": path,
                "size": len(file_data)
            }
        except Exception as e:
            raise Exception(f"Supabase upload failed: {str(e)}")
    
    async def download_file(self, bucket: str, path: str) -> bytes:
        """Download file from Supabase Storage"""
        try:
            result = self.client.storage.from_(bucket).download(path)
            return result
        except Exception as e:
            raise Exception(f"Supabase download failed: {str(e)}")
    
    async def delete_file(self, bucket: str, path: str) -> bool:
        """Delete file from Supabase Storage"""
        try:
            self.client.storage.from_(bucket).remove([path])
            return True
        except Exception as e:
            raise Exception(f"Supabase delete failed: {str(e)}")
    
    async def get_public_url(
        self,
        bucket: str,
        path: str,
        expiration: Optional[int] = None
    ) -> str:
        """Get public or signed URL"""
        try:
            if expiration:
                # Create signed URL with expiration
                signed_url = self.client.storage.from_(bucket).create_signed_url(
                    path=path,
                    expires_in=expiration
                )
                return signed_url['signedURL']
            else:
                # Get public URL
                return self.client.storage.from_(bucket).get_public_url(path)
        except Exception as e:
            raise Exception(f"Supabase URL generation failed: {str(e)}")
    
    async def list_files(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List files in Supabase Storage bucket"""
        try:
            options = {'limit': limit}
            if prefix:
                options['prefix'] = prefix
            
            result = self.client.storage.from_(bucket).list(
                path=prefix or '',
                options=options
            )
            
            files = []
            for file in result:
                if file.get('id'):  # Only include files, not folders
                    files.append({
                        'path': file['name'],
                        'size': file.get('metadata', {}).get('size', 0),
                        'last_modified': file.get('updated_at', file.get('created_at', '')),
                        'id': file['id']
                    })
            
            return files
        except Exception as e:
            raise Exception(f"Supabase list failed: {str(e)}")
    
    async def get_file_metadata(self, bucket: str, path: str) -> Dict[str, Any]:
        """Get file metadata from Supabase Storage"""
        try:
            # Supabase doesn't have a direct metadata endpoint
            # We'll use list with the specific path
            result = self.client.storage.from_(bucket).list(path=path)
            
            if result and len(result) > 0:
                file = result[0]
                metadata = file.get('metadata', {})
                
                return {
                    'size': metadata.get('size', 0),
                    'content_type': metadata.get('mimetype'),
                    'last_modified': file.get('updated_at', file.get('created_at', '')),
                    'id': file.get('id'),
                    'metadata': metadata
                }
            else:
                raise Exception("File not found")
        except Exception as e:
            raise Exception(f"Supabase metadata fetch failed: {str(e)}")
    
    async def create_bucket(
        self,
        name: str,
        public: bool = False,
        region: Optional[str] = None
    ) -> bool:
        """Create Supabase Storage bucket"""
        try:
            self.client.storage.create_bucket(
                name,
                options={'public': public}
            )
            return True
        except Exception as e:
            raise Exception(f"Supabase bucket creation failed: {str(e)}")
    
    async def delete_bucket(self, name: str) -> bool:
        """Delete Supabase Storage bucket"""
        try:
            self.client.storage.delete_bucket(name)
            return True
        except Exception as e:
            raise Exception(f"Supabase bucket deletion failed: {str(e)}")

