"""
Factory for creating logging provider instances.
Supports Datadog, Better Stack, CloudWatch, File, Console, and JSON providers.
"""
from typing import Optional
from core.logging_interface import LoggingProviderInterface
from config import settings


def get_logging_provider(
    provider_name: Optional[str] = None
) -> LoggingProviderInterface:
    """
    Factory function to get the configured logging provider.
    
    Args:
        provider_name: Override the default provider from settings
        
    Returns:
        LoggingProviderInterface implementation
        
    Raises:
        ValueError: If provider is not supported
    """
    provider = provider_name or settings.logging_provider
    
    if provider == "datadog":
        from logging_providers.datadog.provider import DatadogLoggingProvider
        return DatadogLoggingProvider(
            api_key=settings.datadog_api_key,
            app_key=settings.datadog_app_key,
            site=settings.datadog_site
        )
    
    elif provider == "betterstack":
        from logging_providers.betterstack.provider import BetterStackLoggingProvider
        return BetterStackLoggingProvider(
            source_token=settings.betterstack_source_token
        )
    
    elif provider == "cloudwatch":
        from logging_providers.cloudwatch.provider import CloudWatchLoggingProvider
        return CloudWatchLoggingProvider(
            log_group=settings.cloudwatch_log_group,
            log_stream=settings.cloudwatch_log_stream,
            region=settings.aws_region
        )
    
    elif provider == "file":
        from logging_providers.file.provider import FileLoggingProvider
        return FileLoggingProvider(
            log_file_path=settings.log_file_path,
            max_bytes=settings.log_file_max_bytes,
            backup_count=settings.log_file_backup_count
        )
    
    elif provider == "console":
        from logging_providers.console.provider import ConsoleLoggingProvider
        return ConsoleLoggingProvider()
    
    elif provider == "json":
        from logging_providers.json.provider import JSONLoggingProvider
        return JSONLoggingProvider(
            log_file_path=settings.log_file_path
        )
    
    else:
        raise ValueError(
            f"Unsupported logging provider: {provider}. "
            f"Supported: datadog, betterstack, cloudwatch, file, console, json"
        )

