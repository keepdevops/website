import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import stripe
from payment_providers.stripe import StripePaymentProvider
from core.database import Database


@pytest.fixture
def mock_db():
    """Mock database"""
    db = AsyncMock(spec=Database)
    return db


@pytest.fixture
def stripe_provider(mock_db):
    """Create StripePaymentProvider instance"""
    return StripePaymentProvider(mock_db)


class TestStripePaymentProvider:
    
    def test_provider_name(self, stripe_provider):
        """Test provider name"""
        assert stripe_provider.provider_name == "stripe"
    
    @pytest.mark.asyncio
    @patch('stripe.checkout.Session.create')
    async def test_create_checkout_session(self, mock_create, stripe_provider, mock_db):
        """Test Stripe checkout session creation"""
        # Mock database response
        mock_db.get_by_id.return_value = {
            "id": "user_123",
            "email": "test@example.com",
            "stripe_customer_id": "cus_123"
        }
        
        # Mock Stripe response
        mock_create.return_value = MagicMock(
            id="cs_test_123",
            url="https://checkout.stripe.com/test"
        )
        
        result = await stripe_provider.create_checkout_session(
            user_id="user_123",
            price_id="price_123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel"
        )
        
        assert result["session_id"] == "cs_test_123"
        assert result["url"] == "https://checkout.stripe.com/test"
        
        # Verify Stripe was called
        mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('stripe.Customer.create')
    async def test_create_customer(self, mock_create, stripe_provider, mock_db):
        """Test Stripe customer creation"""
        # Mock Stripe response
        mock_create.return_value = MagicMock(id="cus_new_123")
        
        customer_id = await stripe_provider.create_customer(
            user_id="user_123",
            email="test@example.com",
            metadata={"plan": "premium"}
        )
        
        assert customer_id == "cus_new_123"
        
        # Verify database was updated
        mock_db.update_by_id.assert_called_once_with(
            "profiles",
            "user_123",
            {"stripe_customer_id": "cus_new_123"}
        )
    
    @pytest.mark.asyncio
    @patch('stripe.Customer.retrieve')
    async def test_get_customer(self, mock_retrieve, stripe_provider):
        """Test get Stripe customer"""
        mock_retrieve.return_value = MagicMock(
            id="cus_123",
            email="test@example.com",
            metadata={}
        )
        
        customer = await stripe_provider.get_customer("cus_123")
        
        assert customer["id"] == "cus_123"
        assert customer["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    @patch('stripe.Subscription.create')
    async def test_create_subscription(self, mock_create, stripe_provider):
        """Test Stripe subscription creation"""
        from datetime import datetime
        
        mock_create.return_value = MagicMock(
            id="sub_123",
            status="active",
            current_period_end=int(datetime(2025, 12, 31).timestamp())
        )
        
        result = await stripe_provider.create_subscription(
            customer_id="cus_123",
            price_id="price_123"
        )
        
        assert result["subscription_id"] == "sub_123"
        assert result["status"] == "active"
    
    @pytest.mark.asyncio
    @patch('stripe.Subscription.retrieve')
    async def test_get_subscription(self, mock_retrieve, stripe_provider):
        """Test get Stripe subscription"""
        from datetime import datetime
        
        mock_retrieve.return_value = MagicMock(
            id="sub_123",
            status="active",
            current_period_end=int(datetime(2025, 12, 31).timestamp()),
            current_period_start=int(datetime(2025, 12, 1).timestamp()),
            cancel_at_period_end=False,
            canceled_at=None
        )
        
        subscription = await stripe_provider.get_subscription("sub_123")
        
        assert subscription["id"] == "sub_123"
        assert subscription["status"] == "active"
    
    @pytest.mark.asyncio
    @patch('stripe.Subscription.modify')
    async def test_cancel_subscription_at_period_end(self, mock_modify, stripe_provider):
        """Test cancel subscription at period end"""
        mock_modify.return_value = MagicMock(
            id="sub_123",
            status="active",
            cancel_at_period_end=True
        )
        
        result = await stripe_provider.cancel_subscription("sub_123", immediately=False)
        
        assert result["cancel_at_period_end"] is True
        mock_modify.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('stripe.Subscription.delete')
    async def test_cancel_subscription_immediately(self, mock_delete, stripe_provider):
        """Test cancel subscription immediately"""
        mock_delete.return_value = MagicMock(
            id="sub_123",
            status="canceled",
            cancel_at_period_end=False
        )
        
        result = await stripe_provider.cancel_subscription("sub_123", immediately=True)
        
        mock_delete.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('stripe.billing_portal.Session.create')
    async def test_create_billing_portal_session(self, mock_create, stripe_provider):
        """Test billing portal session creation"""
        mock_create.return_value = MagicMock(
            url="https://billing.stripe.com/session/test"
        )
        
        result = await stripe_provider.create_billing_portal_session(
            customer_id="cus_123",
            return_url="https://example.com/dashboard"
        )
        
        assert result["url"] == "https://billing.stripe.com/session/test"
    
    @pytest.mark.asyncio
    @patch('stripe.Price.list')
    async def test_list_prices(self, mock_list, stripe_provider):
        """Test list Stripe prices"""
        mock_price = MagicMock()
        mock_price.id = "price_123"
        mock_price.product.id = "prod_123"
        mock_price.unit_amount = 1000
        mock_price.currency = "usd"
        mock_price.recurring = MagicMock(interval="month")
        mock_price.product.name = "Basic Plan"
        mock_price.product.description = "Basic subscription"
        
        mock_list.return_value = MagicMock(data=[mock_price])
        
        prices = await stripe_provider.list_prices()
        
        assert len(prices) == 1
        assert prices[0]["id"] == "price_123"
        assert prices[0]["unit_amount"] == 1000


