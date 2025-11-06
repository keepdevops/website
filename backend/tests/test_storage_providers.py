"""
Tests for storage provider implementations.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from core.storage_interface import StorageProviderInterface
from storage_providers.aws_s3.provider import AWSS3Provider
from storage_providers.cloudflare_r2.provider import CloudflareR2Provider
from storage_providers.digitalocean_spaces.provider import DigitalOceanSpacesProvider
from storage_providers.backblaze_b2.provider import BackblazeB2Provider
from storage_providers.supabase.provider import SupabaseStorageProvider
from storage_providers.gcs.provider import GoogleCloudStorageProvider
from core.storage_provider_factory import get_storage_provider


class TestStorageProviderInterface:
    """Test storage provider interface compliance"""
    
    def test_interface_methods_exist(self):
        """Verify all required methods exist in interface"""
        required = ['upload_file', 'download_file', 'delete_file', 'get_public_url',
                   'list_files', 'get_file_metadata', 'create_bucket', 'delete_bucket']
        for method in required:
            assert hasattr(StorageProviderInterface, method)


@pytest.mark.asyncio
class TestAWSS3Provider:
    """Test AWS S3 storage provider"""
    
    @patch('storage_providers.aws_s3.provider.boto3')
    async def test_upload_file(self, mock_boto3):
        """Test S3 file upload"""
        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client
        
        provider = AWSS3Provider("test_key", "test_secret", "us-east-1")
        result = await provider.upload_file("test-bucket", "test.txt", b"Hello", "text/plain")
        
        assert result["path"] == "test.txt"
        assert result["size"] == 5
        mock_s3_client.put_object.assert_called_once()
    
    @patch('storage_providers.aws_s3.provider.boto3')
    async def test_download_file(self, mock_boto3):
        """Test S3 file download"""
        mock_s3_client = MagicMock()
        mock_response = {'Body': MagicMock()}
        mock_response['Body'].read.return_value = b"Content"
        mock_s3_client.get_object.return_value = mock_response
        mock_boto3.client.return_value = mock_s3_client
        
        provider = AWSS3Provider("key", "secret")
        data = await provider.download_file("bucket", "file.txt")
        
        assert data == b"Content"


@pytest.mark.asyncio
class TestCloudflareR2Provider:
    """Test Cloudflare R2 storage provider"""
    
    @patch('storage_providers.cloudflare_r2.provider.boto3')
    async def test_upload_with_cdn(self, mock_boto3):
        """Test R2 upload with custom CDN"""
        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client
        
        provider = CloudflareR2Provider(
            "key", "secret",
            "https://account.r2.cloudflarestorage.com",
            cdn_domain="cdn.example.com"
        )
        
        result = await provider.upload_file("bucket", "img.jpg", b"Image")
        assert result["url"] == "https://cdn.example.com/img.jpg"


@pytest.mark.asyncio
class TestDigitalOceanSpacesProvider:
    """Test DigitalOcean Spaces storage provider"""
    
    @patch('storage_providers.digitalocean_spaces.provider.boto3')
    async def test_spaces_cdn_url(self, mock_boto3):
        """Test Spaces CDN URL"""
        mock_boto3.client.return_value = MagicMock()
        
        provider = DigitalOceanSpacesProvider("key", "secret", "nyc3")
        result = await provider.upload_file("space", "file.pdf", b"PDF")
        
        assert "nyc3.cdn.digitaloceanspaces.com" in result["url"]


@pytest.mark.asyncio
class TestBackblazeB2Provider:
    """Test Backblaze B2 storage provider"""
    
    @patch('storage_providers.backblaze_b2.provider.B2Api')
    async def test_b2_upload(self, mock_b2api):
        """Test B2 upload"""
        mock_api = MagicMock()
        mock_bucket = MagicMock()
        mock_api.get_bucket_by_name.return_value = mock_bucket
        mock_api.get_download_url_for_file_name.return_value = "https://dl.url"
        mock_b2api.return_value = mock_api
        
        provider = BackblazeB2Provider("key_id", "key")
        result = await provider.upload_file("bucket", "test.txt", b"Test")
        
        assert result["url"] == "https://dl.url"


@pytest.mark.asyncio
class TestSupabaseStorageProvider:
    """Test Supabase Storage provider"""
    
    @patch('storage_providers.supabase.provider.create_client')
    async def test_supabase_upload(self, mock_create_client):
        """Test Supabase upload"""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_client.storage.from_.return_value = mock_bucket
        mock_bucket.upload.return_value = {"path": "test.jpg"}
        mock_bucket.get_public_url.return_value = "https://supabase.co/test.jpg"
        mock_create_client.return_value = mock_client
        
        provider = SupabaseStorageProvider("https://proj.supabase.co", "key")
        result = await provider.upload_file("uploads", "test.jpg", b"Image")
        
        assert "supabase.co" in result["url"]


@pytest.mark.asyncio
class TestGoogleCloudStorageProvider:
    """Test Google Cloud Storage provider"""
    
    @patch('storage_providers.gcs.provider.storage.Client')
    async def test_gcs_upload(self, mock_storage_client):
        """Test GCS upload"""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.public_url = "https://storage.googleapis.com/bucket/file.txt"
        mock_storage_client.return_value = mock_client
        
        provider = GoogleCloudStorageProvider("project-id")
        result = await provider.upload_file("bucket", "file.txt", b"Content")
        
        assert "googleapis.com" in result["url"]


def test_storage_provider_factory():
    """Test storage provider factory"""
    with patch('core.storage_provider_factory.settings') as mock_settings:
        mock_settings.storage_provider = "aws_s3"
        mock_settings.aws_access_key_id = "key"
        mock_settings.aws_secret_access_key = "secret"
        mock_settings.aws_region = "us-east-1"
        mock_settings.aws_s3_bucket = "bucket"
        
        with patch('storage_providers.aws_s3.provider.boto3'):
            provider = get_storage_provider()
            assert isinstance(provider, AWSS3Provider)
    
    with patch('core.storage_provider_factory.settings') as mock_settings:
        mock_settings.storage_provider = "unsupported"
        with pytest.raises(ValueError, match="Unsupported storage provider"):
            get_storage_provider()


@pytest.mark.asyncio
class TestStorageProviderOperations:
    """Test common provider operations"""
    
    @patch('storage_providers.aws_s3.provider.boto3')
    async def test_delete_file(self, mock_boto3):
        """Test file deletion"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        
        provider = AWSS3Provider("key", "secret")
        success = await provider.delete_file("bucket", "file.txt")
        
        assert success is True
        mock_s3.delete_object.assert_called_once()
    
    @patch('storage_providers.aws_s3.provider.boto3')
    async def test_get_public_url(self, mock_boto3):
        """Test public URL generation"""
        mock_s3 = MagicMock()
        mock_boto3.client.return_value = mock_s3
        
        provider = AWSS3Provider("key", "secret", "us-east-1")
        url = await provider.get_public_url("bucket", "file.txt")
        
        assert "s3" in url
        assert "file.txt" in url
