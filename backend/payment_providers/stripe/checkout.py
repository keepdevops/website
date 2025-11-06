import stripe
from typing import Dict, Any
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class StripeCheckoutService:
    """Handles Stripe checkout session creation and billing portal"""
    
    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription",
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session.
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            mode: 'subscription' or 'payment'
            user_id: Optional user ID for metadata
        
        Returns:
            {
                "session_id": str,
                "url": str
            }
        """
        try:
            metadata = {}
            if user_id:
                metadata["user_id"] = user_id
            
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode=mode,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata
            )
            
            return {
                "session_id": session.id,
                "url": session.url
            }
        
        except stripe.error.StripeError as e:
            logger.error(f"Stripe checkout error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Checkout session creation failed: {str(e)}"
            )
    
    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, str]:
        """
        Create a Stripe billing portal session.
        
        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal session
        
        Returns:
            {"url": str}
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            
            return {"url": session.url}
        
        except stripe.error.StripeError as e:
            logger.error(f"Billing portal error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Portal session creation failed: {str(e)}"
            )


