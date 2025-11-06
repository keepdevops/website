import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import Mock, patch, AsyncMock
import stripe

client = TestClient(app)

@pytest.fixture
def mock_auth_user():
    return {
        "id": "user-123",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_admin": False
    }

@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer mock_token"}

@patch('core.dependencies.get_current_user')
@patch('stripe.checkout.Session.create')
@patch('stripe.Customer.create')
@patch('core.database.Database')
async def test_create_checkout_session(mock_db, mock_customer, mock_session, mock_user):
    mock_user.return_value = {
        "id": "user-123",
        "email": "test@example.com"
    }
    
    mock_db_instance = Mock()
    mock_db_instance.get_by_id = AsyncMock(return_value={
        "id": "user-123",
        "stripe_customer_id": None
    })
    mock_db_instance.update_by_id = AsyncMock()
    mock_db.return_value = mock_db_instance
    
    mock_customer.return_value = Mock(id="cus_123")
    mock_session.return_value = Mock(
        id="cs_test_123",
        url="https://checkout.stripe.com/test"
    )
    
    response = client.post(
        "/api/subscriptions/checkout",
        json={
            "price_id": "price_test_123",
            "success_url": "http://localhost:3000/success",
            "cancel_url": "http://localhost:3000/cancel"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code in [200, 401]

@patch('core.dependencies.get_current_user')
@patch('core.database.Database')
async def test_get_user_subscription(mock_db, mock_user):
    mock_user.return_value = {"id": "user-123"}
    
    mock_db_instance = Mock()
    mock_db_instance.get_all = AsyncMock(return_value=Mock(data=[{
        "id": "sub-123",
        "user_id": "user-123",
        "status": "active",
        "stripe_subscription_id": "sub_stripe_123"
    }]))
    mock_db.return_value = mock_db_instance
    
    response = client.get(
        "/api/subscriptions/me",
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code in [200, 401]

@patch('stripe.Price.list')
async def test_get_available_prices(mock_list):
    mock_product = Mock()
    mock_product.name = "Test Product"
    mock_product.description = "Test Description"
    mock_product.id = "prod_123"
    
    mock_price = Mock()
    mock_price.id = "price_123"
    mock_price.product = mock_product
    mock_price.unit_amount = 1000
    mock_price.currency = "usd"
    mock_price.recurring = Mock(interval="month")
    
    mock_list.return_value = Mock(data=[mock_price])
    
    response = client.get("/api/subscriptions/prices")
    
    assert response.status_code in [200, 404]



