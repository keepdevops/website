from datetime import datetime, timedelta
from typing import List, Optional
from core.database import Database
from core.cache import Cache
from analytics.models import UsageEvent, AnalyticsData, UserActivity
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db
        self.cache = cache
    
    async def track_event(self, event: UsageEvent):
        event_data = {
            "user_id": event.user_id,
            "event_type": event.event_type,
            "metadata": event.metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            await self.db.create("usage_events", event_data)
            
            cache_key = f"user_activity:{event.user_id}"
            await self.cache.increment(cache_key)
            await self.cache.expire(cache_key, 86400)
        
        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}")
    
    async def get_analytics_overview(self) -> AnalyticsData:
        cached = await self.cache.get_json("analytics:overview")
        if cached:
            return AnalyticsData(**cached)
        
        profiles_result = await self.db.get_all("profiles", limit=10000)
        total_users = len(profiles_result.data or [])
        
        subscriptions_result = await self.db.get_all("subscriptions", limit=10000)
        subscriptions = subscriptions_result.data or []
        
        active_subs = sum(1 for sub in subscriptions if sub.get("status") == "active")
        
        analytics = AnalyticsData(
            total_users=total_users,
            active_subscriptions=active_subs,
            monthly_revenue=0.0,
            churn_rate=0.0,
            conversion_rate=(active_subs / total_users * 100) if total_users > 0 else 0.0
        )
        
        await self.cache.set_json("analytics:overview", analytics.model_dump(), expiration=300)
        
        return analytics
    
    async def get_user_activity(self, user_id: str) -> UserActivity:
        downloads_result = await self.db.get_all("download_logs", {"user_id": user_id})
        downloads_count = len(downloads_result.data or [])
        
        subscription_result = await self.db.get_all("subscriptions", {"user_id": user_id}, limit=1)
        subscription_status = None
        if subscription_result.data:
            subscription_status = subscription_result.data[0].get("status")
        
        return UserActivity(
            user_id=user_id,
            last_login=None,
            total_logins=0,
            downloads_count=downloads_count,
            subscription_status=subscription_status
        )
    
    async def get_recent_activity(self, limit: int = 100):
        result = await self.db.get_all("usage_events", limit=limit)
        return result.data or []

