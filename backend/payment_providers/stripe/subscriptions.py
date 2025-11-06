import stripe
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class StripeSubscriptionService:
    """Handles Stripe subscription operations"""
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe subscription.
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            metadata: Optional metadata
        
        Returns:
            {
                "subscription_id": str,
                "status": str,
                "current_period_end": datetime
            }
        """
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {}
            )
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": datetime.fromtimestamp(
                    subscription.current_period_end
                )
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Error creating subscription: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subscription creation failed: {str(e)}"
            )
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve Stripe subscription details.
        
        Args:
            subscription_id: Stripe subscription ID
        
        Returns:
            Subscription data or None
        """
        try:
            sub = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "id": sub.id,
                "status": sub.status,
                "current_period_end": datetime.fromtimestamp(sub.current_period_end),
                "current_period_start": datetime.fromtimestamp(sub.current_period_start),
                "cancel_at_period_end": sub.cancel_at_period_end,
                "canceled_at": datetime.fromtimestamp(sub.canceled_at) if sub.canceled_at else None
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving subscription {subscription_id}: {str(e)}")
            return None
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> Dict[str, Any]:
        """
        Cancel a Stripe subscription.
        
        Args:
            subscription_id: Stripe subscription ID
            immediately: If True, cancel now. If False, at period end
        
        Returns:
            Updated subscription data
        """
        try:
            if immediately:
                sub = stripe.Subscription.delete(subscription_id)
            else:
                sub = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            
            return {
                "id": sub.id,
                "status": sub.status,
                "cancel_at_period_end": sub.cancel_at_period_end
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Error canceling subscription {subscription_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cancellation failed: {str(e)}"
            )
    
    async def list_prices(self) -> List[Dict[str, Any]]:
        """
        List all active Stripe prices.
        
        Returns:
            List of price objects
        """
        try:
            prices = stripe.Price.list(active=True, expand=["data.product"])
            
            price_list = []
            for price in prices.data:
                price_list.append({
                    "id": price.id,
                    "product_id": price.product.id,
                    "unit_amount": price.unit_amount,
                    "currency": price.currency,
                    "recurring_interval": price.recurring.interval if price.recurring else None,
                    "product_name": price.product.name,
                    "product_description": price.product.description
                })
            
            return price_list
        
        except stripe.error.StripeError as e:
            logger.error(f"Error fetching prices: {str(e)}")
            return []


