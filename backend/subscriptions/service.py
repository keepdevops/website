import stripe
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from config import settings
from core.database import Database
from subscriptions.models import (
    SubscriptionCreate, CheckoutSessionCreate, CheckoutSessionResponse,
    BillingPortalSessionCreate, BillingPortalResponse, PriceInfo
)
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.stripe_secret_key

class SubscriptionService:
    def __init__(self, db: Database):
        self.db = db
    
    async def create_checkout_session(
        self,
        user_id: str,
        user_email: str,
        session_data: CheckoutSessionCreate
    ) -> CheckoutSessionResponse:
        try:
            customer = await self._get_or_create_stripe_customer(user_id, user_email)
            
            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card"],
                line_items=[{
                    "price": session_data.price_id,
                    "quantity": 1,
                }],
                mode=session_data.mode,
                success_url=session_data.success_url,
                cancel_url=session_data.cancel_url,
                metadata={"user_id": user_id}
            )
            
            return CheckoutSessionResponse(
                session_id=session.id,
                url=session.url
            )
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe checkout error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Checkout session creation failed: {str(e)}"
            )
    
    async def _get_or_create_stripe_customer(self, user_id: str, email: str):
        existing = await self.db.get_by_id("profiles", user_id)
        
        if existing and existing.get("stripe_customer_id"):
            return stripe.Customer.retrieve(existing["stripe_customer_id"])
        
        customer = stripe.Customer.create(
            email=email,
            metadata={"user_id": user_id}
        )
        
        await self.db.update_by_id("profiles", user_id, {
            "stripe_customer_id": customer.id
        })
        
        return customer
    
    async def get_user_subscription(self, user_id: str) -> Optional[dict]:
        result = await self.db.get_all("subscriptions", {"user_id": user_id}, limit=1)
        
        if result.data and len(result.data) > 0:
            sub_data = result.data[0]
            
            try:
                stripe_sub = stripe.Subscription.retrieve(sub_data["stripe_subscription_id"])
                sub_data["status"] = stripe_sub.status
                sub_data["current_period_end"] = datetime.fromtimestamp(
                    stripe_sub.current_period_end
                ).isoformat()
            except Exception as e:
                logger.error(f"Error fetching Stripe subscription: {str(e)}")
            
            return sub_data
        
        return None
    
    async def cancel_subscription(self, user_id: str, immediately: bool = False):
        subscription = await self.get_user_subscription(user_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        try:
            if immediately:
                stripe.Subscription.delete(subscription["stripe_subscription_id"])
            else:
                stripe.Subscription.modify(
                    subscription["stripe_subscription_id"],
                    cancel_at_period_end=True
                )
            
            await self.db.update_by_id("subscriptions", subscription["id"], {
                "cancel_at_period_end": not immediately,
                "status": "canceled" if immediately else "active"
            })
            
            return {"message": "Subscription cancelled successfully"}
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe cancellation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cancellation failed: {str(e)}"
            )
    
    async def create_billing_portal_session(
        self,
        user_id: str,
        portal_data: BillingPortalSessionCreate
    ) -> BillingPortalResponse:
        profile = await self.db.get_by_id("profiles", user_id)
        
        if not profile or not profile.get("stripe_customer_id"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        try:
            session = stripe.billing_portal.Session.create(
                customer=profile["stripe_customer_id"],
                return_url=portal_data.return_url
            )
            
            return BillingPortalResponse(url=session.url)
        
        except stripe.error.StripeError as e:
            logger.error(f"Billing portal error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Portal session creation failed: {str(e)}"
            )
    
    async def get_available_prices(self) -> List[PriceInfo]:
        try:
            prices = stripe.Price.list(active=True, expand=["data.product"])
            
            price_list = []
            for price in prices.data:
                price_list.append(PriceInfo(
                    id=price.id,
                    product_id=price.product.id,
                    unit_amount=price.unit_amount,
                    currency=price.currency,
                    recurring_interval=price.recurring.interval if price.recurring else None,
                    product_name=price.product.name,
                    product_description=price.product.description
                ))
            
            return price_list
        
        except stripe.error.StripeError as e:
            logger.error(f"Error fetching prices: {str(e)}")
            return []

