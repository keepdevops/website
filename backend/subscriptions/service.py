from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from core.database import Database
from core.payment_interface import PaymentProviderInterface
from subscriptions.models import (
    SubscriptionCreate, CheckoutSessionCreate, CheckoutSessionResponse,
    BillingPortalSessionCreate, BillingPortalResponse, PriceInfo
)
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    def __init__(self, db: Database, payment_provider: PaymentProviderInterface):
        self.db = db
        self.provider = payment_provider
    
    async def create_checkout_session(
        self,
        user_id: str,
        user_email: str,
        session_data: CheckoutSessionCreate
    ) -> CheckoutSessionResponse:
        """Create checkout session using configured payment provider"""
        result = await self.provider.create_checkout_session(
            user_id=user_id,
            price_id=session_data.price_id,
            success_url=session_data.success_url,
            cancel_url=session_data.cancel_url,
            mode=session_data.mode
        )
        
        return CheckoutSessionResponse(
            session_id=result["session_id"],
            url=result["url"]
        )
    
    async def get_user_subscription(self, user_id: str) -> Optional[dict]:
        """Get user subscription from database and enrich with provider data"""
        result = await self.db.get_all("subscriptions", {"user_id": user_id}, limit=1)
        
        if result.data and len(result.data) > 0:
            sub_data = result.data[0]
            
            # Enrich with provider subscription data
            try:
                provider_sub = await self.provider.get_subscription(
                    sub_data["stripe_subscription_id"]
                )
                if provider_sub:
                    sub_data["status"] = provider_sub["status"]
                    sub_data["current_period_end"] = provider_sub["current_period_end"].isoformat()
            except Exception as e:
                logger.error(f"Error fetching provider subscription: {str(e)}")
            
            return sub_data
        
        return None
    
    async def cancel_subscription(self, user_id: str, immediately: bool = False):
        """Cancel subscription using configured payment provider"""
        subscription = await self.get_user_subscription(user_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        # Cancel via payment provider
        result = await self.provider.cancel_subscription(
            subscription_id=subscription["stripe_subscription_id"],
            immediately=immediately
        )
        
        # Update database
        await self.db.update_by_id("subscriptions", subscription["id"], {
            "cancel_at_period_end": not immediately,
            "status": "canceled" if immediately else "active"
        })
        
        return {"message": "Subscription cancelled successfully"}
    
    async def create_billing_portal_session(
        self,
        user_id: str,
        portal_data: BillingPortalSessionCreate
    ) -> BillingPortalResponse:
        """Create billing portal session using configured payment provider"""
        profile = await self.db.get_by_id("profiles", user_id)
        
        if not profile or not profile.get("stripe_customer_id"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        result = await self.provider.create_billing_portal_session(
            customer_id=profile["stripe_customer_id"],
            return_url=portal_data.return_url
        )
        
        return BillingPortalResponse(url=result["url"])
    
    async def get_available_prices(self) -> List[PriceInfo]:
        """Get available prices from configured payment provider"""
        prices = await self.provider.list_prices()
        
        price_list = []
        for price in prices:
            price_list.append(PriceInfo(
                id=price["id"],
                product_id=price["product_id"],
                unit_amount=price["unit_amount"],
                currency=price["currency"],
                recurring_interval=price.get("recurring_interval"),
                product_name=price["product_name"],
                product_description=price.get("product_description")
            ))
        
        return price_list


