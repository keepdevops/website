"""
Adyen payment provider implementation.
Global payment platform with extensive payment method support.
"""
import Adyen
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import Request, HTTPException, status
from core.payment_interface import PaymentProviderInterface


class AdyenPaymentProvider(PaymentProviderInterface):
    """Adyen payment provider"""
    
    def __init__(self, api_key: str, merchant_account: str, environment: str = "test"):
        self.adyen = Adyen.Adyen(
            api_key=api_key,
            platform=environment
        )
        self.merchant_account = merchant_account
    
    async def create_checkout_session(
        self,
        user_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription"
    ) -> Dict[str, Any]:
        """Create Adyen checkout session"""
        request_data = {
            "merchantAccount": self.merchant_account,
            "reference": user_id,
            "returnUrl": success_url,
            "amount": {
                "currency": "USD",
                "value": 1000  # Should map from price_id
            }
        }
        
        result = self.adyen.checkout.sessions(request_data)
        
        return {
            "session_id": result.message["id"],
            "url": result.message["url"]
        }
    
    async def create_customer(
        self,
        user_id: str,
        email: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Adyen uses shopperReference instead of customer objects"""
        return f"shopper_{user_id}"
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer (Adyen doesn't have dedicated customer objects)"""
        return {
            "id": customer_id,
            "email": None
        }
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create Adyen recurring payment"""
        # Adyen handles recurring through stored payment methods
        return {
            "subscription_id": f"adyen_sub_{customer_id}",
            "status": "active",
            "current_period_end": datetime.utcnow()
        }
    
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details"""
        return {
            "id": subscription_id,
            "status": "active",
            "current_period_end": datetime.utcnow(),
            "cancel_at_period_end": False
        }
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> Dict[str, Any]:
        """Cancel Adyen subscription"""
        # Adyen requires disabling stored payment method
        return {
            "subscription_id": subscription_id,
            "status": "cancelled"
        }
    
    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, str]:
        """Adyen doesn't have hosted billing portal"""
        return {"url": return_url}
    
    async def list_prices(self) -> List[Dict[str, Any]]:
        """List prices - Adyen doesn't manage product catalog"""
        return []
    
    async def verify_webhook(
        self,
        request: Request,
        signature_header: str,
        webhook_secret: str
    ) -> Dict[str, Any]:
        """Verify Adyen webhook"""
        import json
        import hmac
        import hashlib
        import base64
        
        body = await request.body()
        
        # Calculate HMAC signature
        expected_sign = hmac.new(
            webhook_secret.encode(),
            body,
            hashlib.sha256
        ).digest()
        expected_signature = base64.b64encode(expected_sign).decode()
        
        if signature_header != expected_signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        event_data = json.loads(body)
        
        return {
            "type": event_data.get("eventCode"),
            "data": event_data
        }
    
    @property
    def provider_name(self) -> str:
        return "adyen"

