"""
AWS S3 storage provider implementation.
Industry standard with full feature set.
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, List, Dict, Any
from datetime import datetime
from core.storage_interface import StorageProviderInterface


class AWSS3Provider(StorageProviderInterface):
    """AWS S3 storage provider"""
    
    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        region: str = "us-east-1",
        default_bucket: Optional[str] = None
    ):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
        self.region = region
        self.default_bucket = default_bucket
    
    async def upload_file(
        self,
        bucket: str,
        path: str,
        file_data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Upload file to S3"""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.put_object(
                Bucket=bucket,
                Key=path,
                Body=file_data,
                **extra_args
            )
            
            url = f"https://{bucket}.s3.{self.region}.amazonaws.com/{path}"
            
            return {
                "url": url,
                "path": path,
                "size": len(file_data)
            }
        except ClientError as e:
            raise Exception(f"S3 upload failed: {str(e)}")
    
    async def download_file(self, bucket: str, path: str) -> bytes:
        """Download file from S3"""
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=path)
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"S3 download failed: {str(e)}")
    
    async def delete_file(self, bucket: str, path: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=path)
            return True
        except ClientError as e:
            raise Exception(f"S3 delete failed: {str(e)}")
    
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
                raise Exception(f"Presigned URL generation failed: {str(e)}")
        else:
            return f"https://{bucket}.s3.{self.region}.amazonaws.com/{path}"
    
    async def list_files(
        self,
        bucket: str,
        prefix: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List files in S3 bucket"""
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
            raise Exception(f"S3 list failed: {str(e)}")
    
    async def get_file_metadata(self, bucket: str, path: str) -> Dict[str, Any]:
        """Get file metadata from S3"""
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
            raise Exception(f"S3 metadata fetch failed: {str(e)}")
    
    async def create_bucket(
        self,
        name: str,
        public: bool = False,
        region: Optional[str] = None
    ) -> bool:
        """Create S3 bucket"""
        try:
            bucket_region = region or self.region
            
            if bucket_region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=name)
            else:
                self.s3_client.create_bucket(
                    Bucket=name,
                    CreateBucketConfiguration={'LocationConstraint': bucket_region}
                )
            
            if public:
                self.s3_client.delete_public_access_block(Bucket=name)
            
            return True
        except ClientError as e:
            raise Exception(f"S3 bucket creation failed: {str(e)}")
    
    async def delete_bucket(self, name: str) -> bool:
        """Delete S3 bucket"""
        try:
            self.s3_client.delete_bucket(Bucket=name)
            return True
        except ClientError as e:
            raise Exception(f"S3 bucket deletion failed: {str(e)}")

