"""
Tests for new payment provider implementations (PayPal, Square, Braintree, Adyen).
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from payment_providers.paypal.provider import PayPalPaymentProvider
from payment_providers.square.provider import SquarePaymentProvider
from payment_providers.braintree.provider import BraintreePaymentProvider
from payment_providers.adyen.provider import AdyenPaymentProvider


@pytest.mark.asyncio
class TestPayPalProvider:
    """Test PayPal payment provider"""
    
    @patch('payment_providers.paypal.provider.httpx.AsyncClient')
    async def test_create_checkout_session(self, mock_client_class):
        """Test PayPal checkout session creation"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "ORDER123",
            "links": [{"rel": "approve", "href": "https://paypal.com/checkout"}]
        }
        
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client
        
        provider = PayPalPaymentProvider("client_id", "secret")
        result = await provider.create_checkout_session(
            "user123", "price_id", "http://success", "http://cancel"
        )
        
        assert result["session_id"] == "ORDER123"
        assert "paypal.com" in result["url"]
    
    async def test_create_customer(self):
        """Test PayPal customer creation (uses email)"""
        provider = PayPalPaymentProvider("client_id", "secret")
        customer_id = await provider.create_customer("user123", "test@example.com")
        
        assert customer_id == "test@example.com"
    
    async def test_provider_name(self):
        """Test provider name property"""
        provider = PayPalPaymentProvider("client_id", "secret")
        assert provider.provider_name == "paypal"


@pytest.mark.asyncio
class TestSquareProvider:
    """Test Square payment provider"""
    
    @patch('payment_providers.square.provider.Client')
    async def test_create_customer(self, mock_client_class):
        """Test Square customer creation"""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.is_success.return_value = True
        mock_result.body = {"customer": {"id": "sq_cust_123"}}
        mock_client.customers.create_customer.return_value = mock_result
        mock_client_class.return_value = mock_client
        
        provider = SquarePaymentProvider("access_token")
        customer_id = await provider.create_customer("user123", "test@example.com")
        
        assert customer_id == "sq_cust_123"
    
    async def test_provider_name(self):
        """Test provider name property"""
        provider = SquarePaymentProvider("access_token")
        assert provider.provider_name == "square"


@pytest.mark.asyncio
class TestBraintreeProvider:
    """Test Braintree payment provider"""
    
    @patch('payment_providers.braintree.provider.braintree')
    async def test_create_customer(self, mock_braintree):
        """Test Braintree customer creation"""
        mock_result = Mock()
        mock_result.is_success = True
        mock_result.customer.id = "bt_cust_123"
        mock_braintree.BraintreeGateway.return_value.customer.create.return_value = mock_result
        
        provider = BraintreePaymentProvider("merchant", "public", "private")
        customer_id = await provider.create_customer("user123", "test@example.com")
        
        assert customer_id == "bt_cust_123"
    
    async def test_provider_name(self):
        """Test provider name property"""
        provider = BraintreePaymentProvider("merchant", "public", "private")
        assert provider.provider_name == "braintree"


@pytest.mark.asyncio
class TestAdyenProvider:
    """Test Adyen payment provider"""
    
    @patch('payment_providers.adyen.provider.Adyen')
    async def test_create_checkout_session(self, mock_adyen_class):
        """Test Adyen checkout session creation"""
        mock_result = Mock()
        mock_result.message = {
            "id": "session123",
            "url": "https://checkoutshopper-test.adyen.com/session123"
        }
        
        mock_adyen = Mock()
        mock_adyen.checkout.sessions.return_value = mock_result
        mock_adyen_class.Adyen.return_value = mock_adyen
        
        provider = AdyenPaymentProvider("api_key", "merchant_account")
        result = await provider.create_checkout_session(
            "user123", "price_id", "http://success", "http://cancel"
        )
        
        assert result["session_id"] == "session123"
        assert "adyen.com" in result["url"]
    
    async def test_provider_name(self):
        """Test provider name property"""
        provider = AdyenPaymentProvider("api_key", "merchant")
        assert provider.provider_name == "adyen"


@pytest.mark.asyncio
class TestAllProvidersCompliance:
    """Test that all providers implement the interface correctly"""
    
    async def test_all_have_required_methods(self):
        """Verify all providers have required methods"""
        required_methods = [
            'create_checkout_session', 'create_customer', 'get_customer',
            'create_subscription', 'get_subscription', 'cancel_subscription',
            'create_billing_portal_session', 'list_prices', 'verify_webhook',
            'provider_name'
        ]
        
        providers = [
            PayPalPaymentProvider("id", "secret"),
            SquarePaymentProvider("token"),
            BraintreePaymentProvider("m", "pub", "priv"),
            AdyenPaymentProvider("key", "merchant")
        ]
        
        for provider in providers:
            for method in required_methods:
                assert hasattr(provider, method), f"{provider.provider_name} missing {method}"

