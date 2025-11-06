from typing import Dict, Any, Optional
from posthog import Posthog
from core.analytics_interface import AnalyticsProviderInterface
import logging

logger = logging.getLogger(__name__)


class PostHogAnalyticsProvider(AnalyticsProviderInterface):
    """PostHog analytics provider (open source product analytics)"""
    
    def __init__(
        self,
        api_key: str,
        host: str = "https://app.posthog.com"
    ):
        self.api_key = api_key
        self.host = host
        self.client = Posthog(
            project_api_key=api_key,
            host=host
        )
        logger.info(f"PostHog initialized: {host}")
    
    @property
    def provider_name(self) -> str:
        return "posthog"
    
    async def track_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track event to PostHog"""
        try:
            distinct_id = user_id or "anonymous"
            
            self.client.capture(
                distinct_id=distinct_id,
                event=event_name,
                properties=properties or {}
            )
            
            logger.info(f"PostHog event tracked: {event_name}")
            return True
        
        except Exception as e:
            logger.error(f"PostHog tracking error: {str(e)}")
            return False
    
    async def track_page_view(
        self,
        user_id: Optional[str],
        page: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track page view to PostHog"""
        props = properties or {}
        props["$current_url"] = page
        
        return await self.track_event(
            "$pageview",
            user_id=user_id,
            properties=props
        )
    
    async def identify_user(
        self,
        user_id: str,
        traits: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Identify user in PostHog"""
        try:
            self.client.identify(
                distinct_id=user_id,
                properties=traits or {}
            )
            
            logger.info(f"PostHog user identified: {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"PostHog identify error: {str(e)}")
            return False
    
    async def track_revenue(
        self,
        user_id: str,
        amount: float,
        currency: str = "usd",
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track revenue in PostHog"""
        props = properties or {}
        props["revenue"] = amount
        props["currency"] = currency
        
        return await self.track_event(
            "purchase",
            user_id=user_id,
            properties=props
        )
    
    def shutdown(self):
        """Shutdown PostHog client"""
        try:
            self.client.shutdown()
        except Exception as e:
            logger.error(f"PostHog shutdown error: {str(e)}")

