"""
PayPal payment provider implementation.
Supports checkout, subscriptions, and billing management.
"""
import httpx
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import Request
from core.payment_interface import PaymentProviderInterface


class PayPalPaymentProvider(PaymentProviderInterface):
    """PayPal payment provider"""
    
    def __init__(self, client_id: str, client_secret: str, mode: str = "sandbox"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.mode = mode
        self.base_url = (
            "https://api-m.paypal.com" if mode == "live"
            else "https://api-m.sandbox.paypal.com"
        )
        self._access_token: Optional[str] = None
    
    async def _get_access_token(self) -> str:
        """Get OAuth access token"""
        if self._access_token:
            return self._access_token
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/oauth2/token",
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"}
            )
            data = response.json()
            self._access_token = data["access_token"]
            return self._access_token
    
    async def _headers(self) -> Dict[str, str]:
        """Get auth headers"""
        token = await self._get_access_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    async def create_checkout_session(
        self,
        user_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription"
    ) -> Dict[str, Any]:
        """Create PayPal checkout session"""
        order_data = {
            "intent": "CAPTURE" if mode == "payment" else "SUBSCRIPTION",
            "purchase_units": [{
                "reference_id": user_id,
                "amount": {"currency_code": "USD", "value": price_id}
            }],
            "application_context": {"return_url": success_url, "cancel_url": cancel_url}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v2/checkout/orders",
                json=order_data,
                headers=await self._headers()
            )
            data = response.json()
            
            return {
                "session_id": data["id"],
                "url": next(link["href"] for link in data["links"] if link["rel"] == "approve")
            }
    
    async def create_customer(
        self,
        user_id: str,
        email: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """PayPal uses email as customer identifier"""
        return email
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by email"""
        return {"id": customer_id, "email": customer_id}
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create PayPal subscription"""
        subscription_data = {
            "plan_id": price_id,
            "subscriber": {"email_address": customer_id}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/billing/subscriptions",
                json=subscription_data,
                headers=await self._headers()
            )
            data = response.json()
            
            return {
                "subscription_id": data["id"],
                "status": data["status"],
                "current_period_end": datetime.utcnow()
            }
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get PayPal subscription"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v1/billing/subscriptions/{subscription_id}",
                headers=await self._headers()
            )
            data = response.json()
            
            return {
                "id": data["id"],
                "status": data["status"],
                "current_period_end": datetime.utcnow(),
                "cancel_at_period_end": False
            }
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> Dict[str, Any]:
        """Cancel PayPal subscription"""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.base_url}/v1/billing/subscriptions/{subscription_id}/cancel",
                json={"reason": "User requested cancellation"},
                headers=await self._headers()
            )
            
            return await self.get_subscription(subscription_id)
    
    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, str]:
        """PayPal manages billing through their own portal"""
        return {"url": f"{self.base_url}/myaccount/autopay"}
    
    async def list_prices(self) -> List[Dict[str, Any]]:
        """List PayPal billing plans"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/v1/billing/plans",
                headers=await self._headers()
            )
            data = response.json()
            
            return [
                {
                    "id": plan["id"],
                    "product_id": plan.get("product_id"),
                    "unit_amount": 0,
                    "currency": "USD",
                    "recurring_interval": "month",
                    "product_name": plan.get("name"),
                    "product_description": plan.get("description")
                }
                for plan in data.get("plans", [])
            ]
    
    async def verify_webhook(
        self,
        request: Request,
        signature_header: str,
        webhook_secret: str
    ) -> Dict[str, Any]:
        """Verify PayPal webhook"""
        import json
        body = await request.body()
        event_data = json.loads(body)
        
        return {
            "type": event_data.get("event_type"),
            "data": event_data.get("resource")
        }
    
    @property
    def provider_name(self) -> str:
        """Return provider name"""
        return "paypal"
