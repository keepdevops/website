from fastapi import APIRouter, Depends, HTTPException, status
from subscriptions.models import (
    CheckoutSessionCreate, CheckoutSessionResponse,
    BillingPortalSessionCreate, BillingPortalResponse,
    SubscriptionCancelRequest, PriceInfo
)
from subscriptions.service import SubscriptionService
from core.database import get_database, Database
from core.dependencies import get_current_user
from core.event_bus import get_event_bus, EventBus
from core.payment_provider_factory import get_payment_provider
from typing import List

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

def get_subscription_service(db: Database = Depends(get_database)) -> SubscriptionService:
    payment_provider = get_payment_provider(db)
    return SubscriptionService(db, payment_provider)

@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    session_data: CheckoutSessionCreate,
    current_user: dict = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    event_bus: EventBus = Depends(get_event_bus)
):
    result = await subscription_service.create_checkout_session(
        current_user["id"],
        current_user["email"],
        session_data
    )
    
    await event_bus.publish("checkout.session_created", {
        "user_id": current_user["id"],
        "session_id": result.session_id
    })
    
    return result

@router.get("/me")
async def get_my_subscription(
    current_user: dict = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    subscription = await subscription_service.get_user_subscription(current_user["id"])
    
    if not subscription:
        return {"status": "no_subscription"}
    
    return subscription

@router.post("/cancel")
async def cancel_subscription(
    cancel_request: SubscriptionCancelRequest,
    current_user: dict = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service),
    event_bus: EventBus = Depends(get_event_bus)
):
    result = await subscription_service.cancel_subscription(
        current_user["id"],
        cancel_request.immediately
    )
    
    await event_bus.publish("subscription.cancelled", {
        "user_id": current_user["id"],
        "immediately": cancel_request.immediately
    })
    
    return result

@router.post("/billing-portal", response_model=BillingPortalResponse)
async def create_billing_portal_session(
    portal_data: BillingPortalSessionCreate,
    current_user: dict = Depends(get_current_user),
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    return await subscription_service.create_billing_portal_session(
        current_user["id"],
        portal_data
    )

@router.get("/prices", response_model=List[PriceInfo])
async def get_available_prices(
    subscription_service: SubscriptionService = Depends(get_subscription_service)
):
    return await subscription_service.get_available_prices()


