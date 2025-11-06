from typing import Dict, Any, Optional
import httpx
from core.analytics_interface import AnalyticsProviderInterface
import logging

logger = logging.getLogger(__name__)


class GoogleAnalyticsProvider(AnalyticsProviderInterface):
    """Google Analytics 4 (GA4) provider implementation"""
    
    def __init__(self, measurement_id: str, api_secret: str):
        self.measurement_id = measurement_id
        self.api_secret = api_secret
        self.base_url = "https://www.google-analytics.com/mp/collect"
    
    @property
    def provider_name(self) -> str:
        return "google_analytics"
    
    async def track_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track event to GA4"""
        try:
            payload = {
                "client_id": user_id or "anonymous",
                "events": [{
                    "name": event_name,
                    "params": properties or {}
                }]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    params={
                        "measurement_id": self.measurement_id,
                        "api_secret": self.api_secret
                    },
                    json=payload,
                    timeout=10
                )
                
                success = response.status_code in [200, 204]
                if success:
                    logger.info(f"GA4 event tracked: {event_name}")
                else:
                    logger.error(f"GA4 error: {response.status_code}")
                
                return success
        
        except Exception as e:
            logger.error(f"GA4 tracking error: {str(e)}")
            return False
    
    async def track_page_view(
        self,
        user_id: Optional[str],
        page: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track page view to GA4"""
        props = properties or {}
        props["page_location"] = page
        
        return await self.track_event(
            "page_view",
            user_id=user_id,
            properties=props
        )
    
    async def identify_user(
        self,
        user_id: str,
        traits: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Identify user in GA4 (via user_properties)"""
        try:
            payload = {
                "client_id": user_id,
                "user_properties": {}
            }
            
            if traits:
                for key, value in traits.items():
                    payload["user_properties"][key] = {"value": value}
            
            payload["events"] = [{
                "name": "user_identify",
                "params": {}
            }]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    params={
                        "measurement_id": self.measurement_id,
                        "api_secret": self.api_secret
                    },
                    json=payload,
                    timeout=10
                )
                
                return response.status_code in [200, 204]
        
        except Exception as e:
            logger.error(f"GA4 identify error: {str(e)}")
            return False
    
    async def track_revenue(
        self,
        user_id: str,
        amount: float,
        currency: str = "usd",
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track purchase/revenue in GA4"""
        props = properties or {}
        props["currency"] = currency.upper()
        props["value"] = amount
        
        return await self.track_event(
            "purchase",
            user_id=user_id,
            properties=props
        )

