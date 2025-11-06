from typing import Dict, Any, Optional
from datetime import datetime
from core.analytics_interface import AnalyticsProviderInterface
from core.database import Database
import logging

logger = logging.getLogger(__name__)


class InternalAnalyticsProvider(AnalyticsProviderInterface):
    """Internal database-based analytics provider"""
    
    def __init__(self, db: Database):
        self.db = db
    
    @property
    def provider_name(self) -> str:
        return "internal"
    
    async def track_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track event to database"""
        try:
            event_data = {
                "event_type": event_name,
                "user_id": user_id,
                "metadata": properties or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.db.create("usage_events", event_data)
            logger.info(f"Internal analytics: {event_name}")
            return True
        
        except Exception as e:
            logger.error(f"Internal analytics error: {str(e)}")
            return False
    
    async def track_page_view(
        self,
        user_id: Optional[str],
        page: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track page view to database"""
        props = properties or {}
        props["page"] = page
        
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
        """Identify user in database (update profile)"""
        try:
            if traits:
                # Update user profile with traits
                await self.db.update_by_id("profiles", user_id, traits)
            
            logger.info(f"User identified: {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"Internal identify error: {str(e)}")
            return False
    
    async def track_revenue(
        self,
        user_id: str,
        amount: float,
        currency: str = "usd",
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track revenue to database"""
        props = properties or {}
        props["amount"] = amount
        props["currency"] = currency
        
        return await self.track_event(
            "purchase",
            user_id=user_id,
            properties=props
        )

