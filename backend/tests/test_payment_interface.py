import pytest
from unittest.mock import AsyncMock, MagicMock
from core.payment_interface import PaymentProviderInterface
from abc import ABC


class MockPaymentProvider(PaymentProviderInterface):
    """Mock payment provider for testing interface contract"""
    
    def __init__(self):
        self.checkout_sessions = {}
        self.customers = {}
        self.subscriptions = {}
        self.prices = []
    
    @property
    def provider_name(self) -> str:
        return "mock"
    
    async def create_checkout_session(self, user_id, price_id, success_url, cancel_url, mode="subscription"):
        session = {
            "session_id": f"mock_session_{user_id}",
            "url": f"https://mock-checkout.com/{user_id}"
        }
        self.checkout_sessions[session["session_id"]] = session
        return session
    
    async def create_customer(self, user_id, email, metadata=None):
        customer_id = f"mock_cus_{user_id}"
        self.customers[customer_id] = {
            "id": customer_id,
            "email": email,
            "metadata": metadata or {}
        }
        return customer_id
    
    async def get_customer(self, customer_id):
        return self.customers.get(customer_id)
    
    async def create_subscription(self, customer_id, price_id, metadata=None):
        from datetime import datetime, timedelta
        sub_id = f"mock_sub_{customer_id}"
        subscription = {
            "subscription_id": sub_id,
            "status": "active",
            "current_period_end": datetime.now() + timedelta(days=30)
        }
        self.subscriptions[sub_id] = subscription
        return subscription
    
    async def get_subscription(self, subscription_id):
        return self.subscriptions.get(subscription_id)
    
    async def cancel_subscription(self, subscription_id, immediately=False):
        if subscription_id in self.subscriptions:
            self.subscriptions[subscription_id]["status"] = "canceled"
            return self.subscriptions[subscription_id]
        return None
    
    async def create_billing_portal_session(self, customer_id, return_url):
        return {"url": f"https://mock-portal.com/{customer_id}?return={return_url}"}
    
    async def list_prices(self):
        return self.prices
    
    async def verify_webhook(self, request, signature_header=None, webhook_secret=None):
        return {
            "type": "mock.event",
            "data": {}
        }


class TestPaymentProviderInterface:
    """Test the abstract payment provider interface contract"""
    
    @pytest.mark.asyncio
    async def test_provider_implements_interface(self):
        """Test that mock provider implements all interface methods"""
        provider = MockPaymentProvider()
        
        # Verify it's an instance of the interface
        assert isinstance(provider, PaymentProviderInterface)
        
        # Verify all methods exist
        assert hasattr(provider, 'create_checkout_session')
        assert hasattr(provider, 'create_customer')
        assert hasattr(provider, 'get_customer')
        assert hasattr(provider, 'create_subscription')
        assert hasattr(provider, 'get_subscription')
        assert hasattr(provider, 'cancel_subscription')
        assert hasattr(provider, 'create_billing_portal_session')
        assert hasattr(provider, 'list_prices')
        assert hasattr(provider, 'verify_webhook')
        assert hasattr(provider, 'provider_name')
    
    @pytest.mark.asyncio
    async def test_create_checkout_session(self):
        """Test checkout session creation"""
        provider = MockPaymentProvider()
        
        result = await provider.create_checkout_session(
            user_id="user_123",
            price_id="price_123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel"
        )
        
        assert "session_id" in result
        assert "url" in result
        assert result["session_id"].startswith("mock_session_")
    
    @pytest.mark.asyncio
    async def test_create_and_get_customer(self):
        """Test customer creation and retrieval"""
        provider = MockPaymentProvider()
        
        customer_id = await provider.create_customer(
            user_id="user_123",
            email="test@example.com",
            metadata={"plan": "premium"}
        )
        
        assert customer_id.startswith("mock_cus_")
        
        customer = await provider.get_customer(customer_id)
        assert customer is not None
        assert customer["email"] == "test@example.com"
        assert customer["metadata"]["plan"] == "premium"
    
    @pytest.mark.asyncio
    async def test_subscription_lifecycle(self):
        """Test subscription creation, retrieval, and cancellation"""
        provider = MockPaymentProvider()
        
        # Create customer first
        customer_id = await provider.create_customer("user_123", "test@example.com")
        
        # Create subscription
        subscription = await provider.create_subscription(
            customer_id=customer_id,
            price_id="price_123"
        )
        
        assert subscription["status"] == "active"
        assert "subscription_id" in subscription
        
        # Get subscription
        retrieved = await provider.get_subscription(subscription["subscription_id"])
        assert retrieved["status"] == "active"
        
        # Cancel subscription
        canceled = await provider.cancel_subscription(subscription["subscription_id"])
        assert canceled["status"] == "canceled"
    
    @pytest.mark.asyncio
    async def test_billing_portal(self):
        """Test billing portal session creation"""
        provider = MockPaymentProvider()
        
        customer_id = await provider.create_customer("user_123", "test@example.com")
        
        result = await provider.create_billing_portal_session(
            customer_id=customer_id,
            return_url="https://example.com/dashboard"
        )
        
        assert "url" in result
        assert result["url"].startswith("https://mock-portal.com")
    
    @pytest.mark.asyncio
    async def test_list_prices(self):
        """Test price listing"""
        provider = MockPaymentProvider()
        
        # Add some mock prices
        provider.prices = [
            {
                "id": "price_1",
                "product_id": "prod_1",
                "unit_amount": 1000,
                "currency": "usd",
                "recurring_interval": "month",
                "product_name": "Basic Plan",
                "product_description": "Basic subscription"
            }
        ]
        
        prices = await provider.list_prices()
        assert len(prices) == 1
        assert prices[0]["id"] == "price_1"
    
    @pytest.mark.asyncio
    async def test_verify_webhook(self):
        """Test webhook verification"""
        provider = MockPaymentProvider()
        
        mock_request = MagicMock()
        result = await provider.verify_webhook(mock_request)
        
        assert "type" in result
        assert "data" in result
    
    def test_provider_name(self):
        """Test provider name property"""
        provider = MockPaymentProvider()
        assert provider.provider_name == "mock"


