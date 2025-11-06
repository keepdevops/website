"""
DigitalOcean Spaces storage provider implementation.
S3-compatible with built-in CDN and flat-rate pricing.
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, List, Dict, Any
from core.storage_interface import StorageProviderInterface


class DigitalOceanSpacesProvider(StorageProviderInterface):
    """DigitalOcean Spaces storage provider (S3-compatible)"""
    
    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        region: str = "nyc3",
        endpoint_url: Optional[str] = None,
        default_bucket: Optional[str] = None,
        cdn_domain: Optional[str] = None
    ):
        # DigitalOcean Spaces endpoint format
        if not endpoint_url:
            endpoint_url = f"https://{region}.digitaloceanspaces.com"
        
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
        self.region = region
        self.endpoint_url = endpoint_url
        self.default_bucket = default_bucket
        self.cdn_domain = cdn_domain
    
    async def upload_file(
        self,
        bucket: str,
        path: str,
        file_data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Upload file to Spaces"""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            if metadata:
                extra_args['Metadata'] = metadata
            
            # Make file publicly accessible
            extra_args['ACL'] = 'public-read'
            
            self.s3_client.put_object(
                Bucket=bucket,
                Key=path,
                Body=file_data,
                **extra_args
            )
            
            # Use CDN domain if provided, otherwise Spaces CDN URL
            if self.cdn_domain:
                url = f"https://{self.cdn_domain}/{path}"
            else:
                url = f"https://{bucket}.{self.region}.cdn.digitaloceanspaces.com/{path}"
            
            return {
                "url": url,
                "path": path,
                "size": len(file_data)
            }
        except ClientError as e:
            raise Exception(f"Spaces upload failed: {str(e)}")
    
    async def download_file(self, bucket: str, path: str) -> bytes:
        """Download file from Spaces"""
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=path)
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Spaces download failed: {str(e)}")
    
    async def delete_file(self, bucket: str, path: str) -> bool:
        """Delete file from Spaces"""
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=path)
            return True
        except ClientError as e:
            raise Exception(f"Spaces delete failed: {str(e)}")
    
    async def get_public_url(
        self,
        bucket: str,
        path: str,
        expiration: Optional[int] = None
    ) -> str:
        """Get public or signed URL"""
        if expiration:
            try:
                url = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket, 'Key': path},
                    ExpiresIn=expiration
                )
                return url
            except ClientError as e:
                raise Exception(f"Spaces presigned URL generation failed: {str(e)}")
        else:
            if self.cdn_domain:
                return f"https://{self.cdn_domain}/{path}"
            else:
                return f"https://{bucket}.{self.region}.cdn.digitaloceanspaces.com/{path}"
    
    async def list_files(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List files in Spaces bucket"""
        try:
            params = {'Bucket': bucket, 'MaxKeys': limit}
            if prefix:
                params['Prefix'] = prefix
            
            response = self.s3_client.list_objects_v2(**params)
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'path': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag']
                })
            
            return files
        except ClientError as e:
            raise Exception(f"Spaces list failed: {str(e)}")
    
    async def get_file_metadata(self, bucket: str, path: str) -> Dict[str, Any]:
        """Get file metadata from Spaces"""
        try:
            response = self.s3_client.head_object(Bucket=bucket, Key=path)
            
            return {
                'size': response['ContentLength'],
                'content_type': response.get('ContentType'),
                'last_modified': response['LastModified'].isoformat(),
                'etag': response['ETag'],
                'metadata': response.get('Metadata', {})
            }
        except ClientError as e:
            raise Exception(f"Spaces metadata fetch failed: {str(e)}")
    
    async def create_bucket(
        self,
        name: str,
        public: bool = False,
        region: Optional[str] = None
    ) -> bool:
        """Create Spaces bucket"""
        try:
            self.s3_client.create_bucket(Bucket=name)
            
            if public:
                # Make bucket publicly readable
                self.s3_client.put_bucket_acl(Bucket=name, ACL='public-read')
            
            return True
        except ClientError as e:
            raise Exception(f"Spaces bucket creation failed: {str(e)}")
    
    async def delete_bucket(self, name: str) -> bool:
        """Delete Spaces bucket"""
        try:
            self.s3_client.delete_bucket(Bucket=name)
            return True
        except ClientError as e:
            raise Exception(f"Spaces bucket deletion failed: {str(e)}")

