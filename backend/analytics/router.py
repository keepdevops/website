from fastapi import APIRouter, Depends
from analytics.models import UsageEvent, AnalyticsData, UserActivity
from analytics.service import AnalyticsService
from core.database import get_database, Database
from core.cache import get_cache, Cache
from core.dependencies import get_current_user, get_current_admin_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

def get_analytics_service(
    db: Database = Depends(get_database),
    cache: Cache = Depends(get_cache)
) -> AnalyticsService:
    return AnalyticsService(db, cache)

@router.post("/track")
async def track_event(
    event: UsageEvent,
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    event.user_id = current_user["id"]
    await analytics_service.track_event(event)
    return {"status": "tracked"}

@router.get("/overview", response_model=AnalyticsData)
async def get_analytics_overview(
    current_user: dict = Depends(get_current_admin_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return await analytics_service.get_analytics_overview()

@router.get("/user-activity", response_model=UserActivity)
async def get_user_activity(
    current_user: dict = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return await analytics_service.get_user_activity(current_user["id"])

@router.get("/recent-activity")
async def get_recent_activity(
    current_user: dict = Depends(get_current_admin_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    activities = await analytics_service.get_recent_activity()
    return {"activities": activities}



