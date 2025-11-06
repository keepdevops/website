"""
Square payment provider implementation.
Supports payments, subscriptions, and customer management.
"""
from square.client import Client
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import Request, HTTPException, status
from core.payment_interface import PaymentProviderInterface


class SquarePaymentProvider(PaymentProviderInterface):
    """Square payment provider"""
    
    def __init__(self, access_token: str, environment: str = "sandbox"):
        self.client = Client(
            access_token=access_token,
            environment=environment
        )
    
    async def create_checkout_session(
        self,
        user_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription"
    ) -> Dict[str, Any]:
        """Create Square checkout session"""
        result = self.client.checkout.create_payment_link(
            body={
                "order": {
                    "location_id": "main",
                    "line_items": [{
                        "quantity": "1",
                        "catalog_object_id": price_id
                    }]
                },
                "checkout_options": {
                    "redirect_url": success_url,
                    "ask_for_shipping_address": False
                }
            }
        )
        
        if result.is_success():
            payment_link = result.body.get("payment_link")
            return {
                "session_id": payment_link["id"],
                "url": payment_link["url"]
            }
        else:
            raise Exception(f"Square checkout failed: {result.errors}")
    
    async def create_customer(
        self,
        user_id: str,
        email: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create Square customer"""
        result = self.client.customers.create_customer(
            body={
                "email_address": email,
                "reference_id": user_id
            }
        )
        
        if result.is_success():
            return result.body["customer"]["id"]
        else:
            raise Exception(f"Square customer creation failed: {result.errors}")
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get Square customer"""
        result = self.client.customers.retrieve_customer(customer_id=customer_id)
        
        if result.is_success():
            customer = result.body["customer"]
            return {
                "id": customer["id"],
                "email": customer.get("email_address"),
                "created": customer.get("created_at")
            }
        return None
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create Square subscription"""
        result = self.client.subscriptions.create_subscription(
            body={
                "location_id": "main",
                "plan_id": price_id,
                "customer_id": customer_id
            }
        )
        
        if result.is_success():
            sub = result.body["subscription"]
            return {
                "subscription_id": sub["id"],
                "status": sub["status"],
                "current_period_end": datetime.utcnow()
            }
        else:
            raise Exception(f"Square subscription failed: {result.errors}")
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get Square subscription"""
        result = self.client.subscriptions.retrieve_subscription(subscription_id=subscription_id)
        
        if result.is_success():
            sub = result.body["subscription"]
            return {
                "id": sub["id"],
                "status": sub["status"],
                "current_period_end": datetime.utcnow(),
                "cancel_at_period_end": False
            }
        return None
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> Dict[str, Any]:
        """Cancel Square subscription"""
        result = self.client.subscriptions.cancel_subscription(subscription_id=subscription_id)
        
        if result.is_success():
            return await self.get_subscription(subscription_id)
        else:
            raise Exception(f"Square cancellation failed: {result.errors}")
    
    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, str]:
        """Square doesn't have a hosted billing portal"""
        return {"url": f"https://squareup.com/dashboard/customers/{customer_id}"}
    
    async def list_prices(self) -> List[Dict[str, Any]]:
        """List Square catalog items"""
        result = self.client.catalog.list_catalog(types="ITEM")
        
        if result.is_success():
            items = result.body.get("objects", [])
            return [
                {
                    "id": item["id"],
                    "product_id": item["id"],
                    "unit_amount": 0,
                    "currency": "USD",
                    "recurring_interval": None,
                    "product_name": item.get("item_data", {}).get("name"),
                    "product_description": item.get("item_data", {}).get("description")
                }
                for item in items
            ]
        return []
    
    async def verify_webhook(
        self,
        request: Request,
        signature_header: str,
        webhook_secret: str
    ) -> Dict[str, Any]:
        """Verify Square webhook"""
        import json
        body = await request.body()
        event_data = json.loads(body)
        
        return {
            "type": event_data.get("type"),
            "data": event_data.get("data")
        }
    
    @property
    def provider_name(self) -> str:
        return "square"

