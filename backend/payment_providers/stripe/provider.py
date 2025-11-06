from typing import Dict, Any, List, Optional
from fastapi import Request
from core.payment_interface import PaymentProviderInterface
from core.database import Database
from .checkout import StripeCheckoutService
from .customers import StripeCustomerService
from .subscriptions import StripeSubscriptionService
from .webhooks import StripeWebhookService
from .config import get_stripe_config
import logging

logger = logging.getLogger(__name__)


class StripePaymentProvider(PaymentProviderInterface):
    """Stripe implementation of PaymentProviderInterface"""
    
    def __init__(self, db: Database):
        self.db = db
        self.config = get_stripe_config()
        
        # Initialize service modules
        self.checkout_service = StripeCheckoutService()
        self.customer_service = StripeCustomerService(db)
        self.subscription_service = StripeSubscriptionService()
        self.webhook_service = StripeWebhookService(self.config["webhook_secret"])
        
        logger.info("StripePaymentProvider initialized")
    
    @property
    def provider_name(self) -> str:
        return "stripe"
    
    async def create_checkout_session(
        self,
        user_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription"
    ) -> Dict[str, Any]:
        """Create Stripe checkout session"""
        # Get user email
        user = await self.db.get_by_id("profiles", user_id)
        email = user.get("email") if user else None
        
        # Get or create customer
        customer_id = await self.customer_service.get_or_create_customer(
            user_id=user_id,
            email=email
        )
        
        # Create checkout session
        return await self.checkout_service.create_checkout_session(
            customer_id=customer_id,
            price_id=price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            mode=mode,
            user_id=user_id
        )
    
    async def create_customer(
        self,
        user_id: str,
        email: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create Stripe customer"""
        return await self.customer_service.create_customer(
            user_id=user_id,
            email=email,
            metadata=metadata
        )
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get Stripe customer"""
        return await self.customer_service.get_customer(customer_id)
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create Stripe subscription"""
        return await self.subscription_service.create_subscription(
            customer_id=customer_id,
            price_id=price_id,
            metadata=metadata
        )
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get Stripe subscription"""
        return await self.subscription_service.get_subscription(subscription_id)
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> Dict[str, Any]:
        """Cancel Stripe subscription"""
        return await self.subscription_service.cancel_subscription(
            subscription_id=subscription_id,
            immediately=immediately
        )
    
    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, str]:
        """Create Stripe billing portal session"""
        return await self.checkout_service.create_billing_portal_session(
            customer_id=customer_id,
            return_url=return_url
        )
    
    async def list_prices(self) -> List[Dict[str, Any]]:
        """List Stripe prices"""
        return await self.subscription_service.list_prices()
    
    async def verify_webhook(
        self,
        request: Request,
        signature_header: str = None,
        webhook_secret: str = None
    ) -> Dict[str, Any]:
        """Verify Stripe webhook"""
        return await self.webhook_service.verify_webhook(
            request=request,
            signature_header=signature_header
        )


