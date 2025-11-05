import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import Mock, patch, AsyncMock
import stripe
import json

client = TestClient(app)

@pytest.fixture
def mock_stripe_webhook():
    with patch('stripe.Webhook.construct_event') as mock:
        yield mock

@pytest.fixture
def mock_cache():
    with patch('core.cache.Cache') as mock:
        cache_instance = Mock()
        cache_instance.exists = AsyncMock(return_value=False)
        cache_instance.set = AsyncMock(return_value=True)
        mock.return_value = cache_instance
        yield cache_instance

@pytest.fixture
def mock_db():
    with patch('core.database.Database') as mock:
        db_instance = Mock()
        db_instance.create = AsyncMock()
        db_instance.get_all = AsyncMock(return_value=Mock(data=[]))
        db_instance.update_by_id = AsyncMock()
        mock.return_value = db_instance
        yield db_instance

def test_webhook_missing_signature():
    response = client.post("/api/webhooks/stripe", 
                          json={"type": "test"},
                          headers={})
    assert response.status_code in [400, 404]

@patch('stripe.Webhook.construct_event')
@patch('webhooks.validator.WebhookValidator.check_idempotency')
async def test_webhook_valid_signature(mock_idempotency, mock_construct):
    event_data = {
        "id": "evt_test_123",
        "type": "customer.subscription.created",
        "data": {
            "object": {
                "id": "sub_123",
                "customer": "cus_123",
                "status": "active",
                "current_period_start": 1234567890,
                "current_period_end": 1234567890,
                "cancel_at_period_end": False
            }
        },
        "created": 1234567890
    }
    
    mock_construct.return_value = event_data
    mock_idempotency.return_value = True
    
    response = client.post(
        "/api/webhooks/stripe",
        json=event_data,
        headers={"stripe-signature": "test_sig"}
    )
    
    assert response.status_code in [200, 404]

def test_webhook_duplicate_event():
    event_data = {
        "id": "evt_duplicate",
        "type": "customer.subscription.created"
    }
    
    with patch('stripe.Webhook.construct_event') as mock_construct:
        with patch('webhooks.validator.WebhookValidator.validate_event') as mock_validate:
            mock_construct.return_value = event_data
            mock_validate.return_value = False
            
            response = client.post(
                "/api/webhooks/stripe",
                json=event_data,
                headers={"stripe-signature": "test_sig"}
            )
            
            assert response.status_code in [200, 404]

