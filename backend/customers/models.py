from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class CustomerProfile(BaseModel):
    id: str
    email: str
    full_name: str
    stripe_customer_id: Optional[str] = None
    subscription_status: Optional[str] = None
    created_at: datetime
    is_admin: bool = False

class CustomerList(BaseModel):
    customers: List[CustomerProfile]
    total: int
    page: int
    page_size: int

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    is_admin: Optional[bool] = None

class CustomerStats(BaseModel):
    total_customers: int
    active_subscriptions: int
    canceled_subscriptions: int
    trial_subscriptions: int
    monthly_recurring_revenue: float

class CustomerSearch(BaseModel):
    query: Optional[str] = None
    subscription_status: Optional[str] = None
    is_admin: Optional[bool] = None
    page: int = 1
    page_size: int = 50



