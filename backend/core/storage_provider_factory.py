"""
Factory for creating storage provider instances.
Supports AWS S3, Cloudflare R2, DigitalOcean Spaces, Backblaze B2, Supabase, and GCS.
"""
from typing import Optional
from core.storage_interface import StorageProviderInterface
from config import settings


def get_storage_provider(provider_name: Optional[str] = None) -> StorageProviderInterface:
    """
    Factory function to get the configured storage provider.
    
    Args:
        provider_name: Override the default provider from settings
        
    Returns:
        StorageProviderInterface implementation
        
    Raises:
        ValueError: If provider is not supported
    """
    provider = provider_name or settings.storage_provider
    
    if provider == "aws_s3":
        from storage_providers.aws_s3.provider import AWSS3Provider
        return AWSS3Provider(
            access_key_id=settings.aws_access_key_id,
            secret_access_key=settings.aws_secret_access_key,
            region=settings.aws_region,
            default_bucket=settings.aws_s3_bucket
        )
    
    elif provider == "cloudflare_r2":
        from storage_providers.cloudflare_r2.provider import CloudflareR2Provider
        return CloudflareR2Provider(
            access_key_id=settings.aws_access_key_id,
            secret_access_key=settings.aws_secret_access_key,
            endpoint_url=settings.s3_endpoint_url,
            default_bucket=settings.aws_s3_bucket,
            cdn_domain=settings.cdn_domain
        )
    
    elif provider == "digitalocean_spaces":
        from storage_providers.digitalocean_spaces.provider import DigitalOceanSpacesProvider
        return DigitalOceanSpacesProvider(
            access_key_id=settings.aws_access_key_id,
            secret_access_key=settings.aws_secret_access_key,
            region=settings.aws_region,
            endpoint_url=settings.s3_endpoint_url,
            default_bucket=settings.aws_s3_bucket,
            cdn_domain=settings.cdn_domain
        )
    
    elif provider == "backblaze_b2":
        from storage_providers.backblaze_b2.provider import BackblazeB2Provider
        return BackblazeB2Provider(
            application_key_id=settings.b2_application_key_id,
            application_key=settings.b2_application_key,
            default_bucket=settings.b2_bucket_name
        )
    
    elif provider == "supabase":
        from storage_providers.supabase.provider import SupabaseStorageProvider
        return SupabaseStorageProvider(
            url=settings.supabase_url,
            key=settings.supabase_service_key,
            default_bucket=settings.supabase_storage_bucket
        )
    
    elif provider == "gcs":
        from storage_providers.gcs.provider import GoogleCloudStorageProvider
        return GoogleCloudStorageProvider(
            project_id=settings.gcs_project_id,
            credentials_path=settings.gcs_credentials_path,
            default_bucket=settings.gcs_bucket_name
        )
    
    else:
        raise ValueError(
            f"Unsupported storage provider: {provider}. "
            f"Supported: aws_s3, cloudflare_r2, digitalocean_spaces, backblaze_b2, supabase, gcs"
        )

