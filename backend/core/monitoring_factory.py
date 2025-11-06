from typing import List, Optional
from core.monitoring_interface import MonitoringProviderInterface
from config import settings
import logging

logger = logging.getLogger(__name__)


def get_monitoring_providers() -> List[MonitoringProviderInterface]:
    """
    Get monitoring provider instances based on configuration.
    
    Supports multiple providers simultaneously.
    
    Returns:
        List of MonitoringProviderInterface implementations
    """
    providers = []
    
    provider_names = getattr(settings, 'monitoring_providers', ['console'])
    if isinstance(provider_names, str):
        provider_names = [p.strip() for p in provider_names.split(',')]
    
    for provider_name in provider_names:
        try:
            provider = _get_single_provider(provider_name)
            if provider:
                providers.append(provider)
                logger.info(f"Loaded monitoring provider: {provider_name}")
        except Exception as e:
            logger.error(f"Failed to load monitoring provider {provider_name}: {str(e)}")
    
    return providers


def _get_single_provider(provider_name: str) -> Optional[MonitoringProviderInterface]:
    """Get a single monitoring provider by name"""
    
    if provider_name == "sentry":
        dsn = getattr(settings, 'sentry_dsn', None)
        if not dsn:
            logger.warning("Sentry DSN not configured, skipping")
            return None
        
        from monitoring_providers.sentry import SentryMonitoringProvider
        return SentryMonitoringProvider(
            dsn=dsn,
            environment=getattr(settings, 'environment', 'production'),
            traces_sample_rate=getattr(settings, 'sentry_traces_sample_rate', 0.1)
        )
    
    elif provider_name == "console":
        from monitoring_providers.console import ConsoleMonitoringProvider
        return ConsoleMonitoringProvider()
    
    # Future providers:
    # elif provider_name == "logrocket":
    #     from monitoring_providers.logrocket import LogRocketMonitoringProvider
    #     return LogRocketMonitoringProvider(...)
    # elif provider_name == "datadog":
    #     from monitoring_providers.datadog import DatadogMonitoringProvider
    #     return DatadogMonitoringProvider(...)
    
    else:
        logger.warning(f"Unknown monitoring provider: {provider_name}")
        return None

