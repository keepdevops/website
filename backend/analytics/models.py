from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UsageEvent(BaseModel):
    user_id: str
    event_type: str
    metadata: Optional[dict] = None

class AnalyticsData(BaseModel):
    total_users: int
    active_subscriptions: int
    monthly_revenue: float
    churn_rate: float
    conversion_rate: float

class UserActivity(BaseModel):
    user_id: str
    last_login: Optional[datetime] = None
    total_logins: int
    downloads_count: int
    subscription_status: Optional[str] = None

