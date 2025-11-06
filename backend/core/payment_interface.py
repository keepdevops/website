from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from fastapi import Request
from datetime import datetime


class PaymentProviderInterface(ABC):
    """Abstract interface for payment providers (Stripe, PayPal, Square, etc.)"""
    
    @abstractmethod
    async def create_checkout_session(
        self,
        user_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        mode: str = "subscription"
    ) -> Dict[str, Any]:
        """
        Create a checkout session for payment.
        
        Returns:
            {
                "session_id": str,
                "url": str  # URL to redirect user to
            }
        """
        pass
    
    @abstractmethod
    async def create_customer(
        self,
        user_id: str,
        email: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a customer in the payment provider.
        
        Returns:
            customer_id: External customer ID from provider
        """
        pass
    
    @abstractmethod
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve customer details from payment provider.
        
        Returns:
            Customer object or None if not found
        """
        pass
    
    @abstractmethod
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a subscription for a customer.
        
        Returns:
            {
                "subscription_id": str,
                "status": str,
                "current_period_end": datetime
            }
        """
        pass
    
    @abstractmethod
    async def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve subscription details.
        
        Returns:
            {
                "id": str,
                "status": str,
                "current_period_end": datetime,
                "cancel_at_period_end": bool
            }
        """
        pass
    
    @abstractmethod
    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False
    ) -> Dict[str, Any]:
        """
        Cancel a subscription.
        
        Args:
            immediately: If True, cancel now. If False, cancel at period end.
        
        Returns:
            Updated subscription data
        """
        pass
    
    @abstractmethod
    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, str]:
        """
        Create a billing portal session for customer to manage their subscription.
        
        Returns:
            {"url": str}  # URL to redirect customer to
        """
        pass
    
    @abstractmethod
    async def list_prices(self) -> List[Dict[str, Any]]:
        """
        List all available prices/plans.
        
        Returns:
            List of price objects with structure:
            [
                {
                    "id": str,
                    "product_id": str,
                    "unit_amount": int,
                    "currency": str,
                    "recurring_interval": Optional[str],
                    "product_name": str,
                    "product_description": Optional[str]
                }
            ]
        """
        pass
    
    @abstractmethod
    async def verify_webhook(
        self,
        request: Request,
        signature_header: str,
        webhook_secret: str
    ) -> Dict[str, Any]:
        """
        Verify webhook signature and return event data.
        
        Returns:
            {
                "type": str,  # Event type (e.g., "customer.subscription.created")
                "data": dict  # Event data
            }
        
        Raises:
            HTTPException: If signature verification fails
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this payment provider (e.g., 'stripe', 'paypal')"""
        pass


