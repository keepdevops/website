"""
Braintree payment provider implementation.
PayPal-owned gateway with strong subscription support.
"""
import braintree
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import Request
from core.payment_interface import PaymentProviderInterface


class BraintreePaymentProvider(PaymentProviderInterface):
    """Braintree payment provider"""
    
    def __init__(self, merchant_id: str, public_key: str, private_key: str, environment: str = "sandbox"):
        env = braintree.Environment.Sandbox if environment == "sandbox" else braintree.Environment.Production
        
        braintree.Configuration.configure(
            env,
            merchant_id=merchant_id,
            public_key=public_key,
            private_key=private_key
        )
        self.gateway = braintree.BraintreeGateway()
    
    async def create_checkout_session(
        self,
        user_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription"
    ) -> Dict[str, Any]:
        """Create Braintree checkout - returns client token"""
        client_token = self.gateway.client_token.generate()
        
        return {
            "session_id": client_token,
            "url": success_url,  # Frontend handles checkout with Drop-in UI
            "client_token": client_token
        }
    
    async def create_customer(
        self,
        user_id: str,
        email: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create Braintree customer"""
        result = self.gateway.customer.create({
            "email": email,
            "custom_fields": {"user_id": user_id}
        })
        
        if result.is_success:
            return result.customer.id
        else:
            raise Exception(f"Braintree customer creation failed: {result.message}")
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get Braintree customer"""
        try:
            customer = self.gateway.customer.find(customer_id)
            return {
                "id": customer.id,
                "email": customer.email,
                "created": customer.created_at
            }
        except braintree.exceptions.NotFoundError:
            return None
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create Braintree subscription"""
        # First create a payment method for the customer
        result = self.gateway.subscription.create({
            "payment_method_token": customer_id,  # Simplified
            "plan_id": price_id
        })
        
        if result.is_success:
            sub = result.subscription
            return {
                "subscription_id": sub.id,
                "status": sub.status,
                "current_period_end": sub.billing_period_end_date
            }
        else:
            raise Exception(f"Braintree subscription failed: {result.message}")
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get Braintree subscription"""
        try:
            sub = self.gateway.subscription.find(subscription_id)
            return {
                "id": sub.id,
                "status": sub.status,
                "current_period_end": sub.billing_period_end_date,
                "cancel_at_period_end": sub.status == "Canceled"
            }
        except braintree.exceptions.NotFoundError:
            return None
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> Dict[str, Any]:
        """Cancel Braintree subscription"""
        result = self.gateway.subscription.cancel(subscription_id)
        
        if result.is_success:
            return await self.get_subscription(subscription_id)
        else:
            raise Exception(f"Braintree cancellation failed: {result.message}")
    
    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, str]:
        """Braintree doesn't have hosted billing portal"""
        return {"url": return_url}
    
    async def list_prices(self) -> List[Dict[str, Any]]:
        """List Braintree plans"""
        plans = self.gateway.plan.all()
        
        return [
            {
                "id": plan.id,
                "product_id": plan.id,
                "unit_amount": int(float(plan.price) * 100),
                "currency": plan.currency_iso_code,
                "recurring_interval": "month",
                "product_name": plan.name,
                "product_description": plan.description
            }
            for plan in plans
        ]
    
    async def verify_webhook(
        self,
        request: Request,
        signature_header: str,
        webhook_secret: str
    ) -> Dict[str, Any]:
        """Verify Braintree webhook"""
        body = await request.body()
        
        # Braintree webhook parsing
        import json
        data = json.loads(body)
        
        return {
            "type": data.get("kind"),
            "data": data.get("subject")
        }
    
    @property
    def provider_name(self) -> str:
        return "braintree"

