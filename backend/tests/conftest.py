import pytest
import asyncio
from typing import Generator

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_user_data():
    return {
        "id": "user-test-123",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_admin": False,
        "created_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def mock_admin_data():
    return {
        "id": "admin-test-123",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "is_admin": True,
        "created_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def mock_subscription_data():
    return {
        "id": "sub-123",
        "user_id": "user-test-123",
        "stripe_customer_id": "cus_123",
        "stripe_subscription_id": "sub_stripe_123",
        "status": "active",
        "current_period_start": "2024-01-01T00:00:00Z",
        "current_period_end": "2024-02-01T00:00:00Z",
        "cancel_at_period_end": False
    }



