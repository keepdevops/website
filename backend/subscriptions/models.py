from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class SubscriptionCreate(BaseModel):
    price_id: str
    payment_method_id: Optional[str] = None

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    stripe_customer_id: str
    stripe_subscription_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    product_name: str
    price_amount: int
    currency: str

class SubscriptionUpdate(BaseModel):
    price_id: Optional[str] = None
    cancel_at_period_end: Optional[bool] = None

class CheckoutSessionCreate(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str
    mode: Literal["subscription", "payment"] = "subscription"

class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str

class PriceInfo(BaseModel):
    id: str
    product_id: str
    unit_amount: int
    currency: str
    recurring_interval: Optional[str] = None
    product_name: str
    product_description: Optional[str] = None

class BillingPortalSessionCreate(BaseModel):
    return_url: str

class BillingPortalResponse(BaseModel):
    url: str

class SubscriptionCancelRequest(BaseModel):
    immediately: bool = False

