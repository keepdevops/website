from typing import List, Optional
from core.analytics_interface import AnalyticsProviderInterface
from core.database import Database
from config import settings
import logging

logger = logging.getLogger(__name__)


def get_analytics_providers(db: Database) -> List[AnalyticsProviderInterface]:
    """
    Get analytics provider instances based on configuration.
    
    Supports multiple providers simultaneously.
    
    Args:
        db: Database instance (needed for internal provider)
    
    Returns:
        List of AnalyticsProviderInterface implementations
    """
    providers = []
    
    provider_names = getattr(settings, 'analytics_providers', ['internal'])
    if isinstance(provider_names, str):
        provider_names = [p.strip() for p in provider_names.split(',')]
    
    for provider_name in provider_names:
        try:
            provider = _get_single_provider(provider_name, db)
            if provider:
                providers.append(provider)
                logger.info(f"Loaded analytics provider: {provider_name}")
        except Exception as e:
            logger.error(f"Failed to load analytics provider {provider_name}: {str(e)}")
    
    return providers


def _get_single_provider(provider_name: str, db: Database) -> Optional[AnalyticsProviderInterface]:
    """Get a single analytics provider by name"""
    
    if provider_name == "google_analytics":
        measurement_id = getattr(settings, 'google_analytics_measurement_id', None)
        api_secret = getattr(settings, 'google_analytics_api_secret', None)
        
        if not measurement_id or not api_secret:
            logger.warning("Google Analytics credentials not configured, skipping")
            return None
        
        from analytics_providers.google_analytics import GoogleAnalyticsProvider
        return GoogleAnalyticsProvider(
            measurement_id=measurement_id,
            api_secret=api_secret
        )
    
    elif provider_name == "posthog":
        api_key = getattr(settings, 'posthog_api_key', None)
        
        if not api_key:
            logger.warning("PostHog API key not configured, skipping")
            return None
        
        from analytics_providers.posthog import PostHogAnalyticsProvider
        return PostHogAnalyticsProvider(
            api_key=api_key,
            host=getattr(settings, 'posthog_host', 'https://app.posthog.com')
        )
    
    elif provider_name == "internal":
        from analytics_providers.internal import InternalAnalyticsProvider
        return InternalAnalyticsProvider(db=db)
    
    # Future providers:
    # elif provider_name == "mixpanel":
    #     from analytics_providers.mixpanel import MixpanelAnalyticsProvider
    #     return MixpanelAnalyticsProvider(...)
    # elif provider_name == "plausible":
    #     from analytics_providers.plausible import PlausibleAnalyticsProvider
    #     return PlausibleAnalyticsProvider(...)
    
    else:
        logger.warning(f"Unknown analytics provider: {provider_name}")
        return None

