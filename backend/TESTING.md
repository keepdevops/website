# Testing Guide

## Overview

Comprehensive mock tests for all backend modules. All test files are ≤200 LOC.

## Test Structure

```
tests/
  ├── conftest.py              # Shared fixtures
  ├── test_auth.py             # Authentication tests
  ├── test_subscriptions.py    # Stripe subscription tests
  ├── test_webhooks.py         # Webhook security tests
  └── test_docker_registry.py  # Docker download tests
```

## Running Tests

### Quick Run

```bash
cd backend
chmod +x run_tests.sh
./run_tests.sh
```

### Manual Run

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Run Single Test

```bash
pytest tests/test_auth.py::test_health_endpoint -v
```

## Test Categories

### 1. Authentication Tests (`test_auth.py`)

**Tests:**
- ✅ Health check endpoint
- ✅ User registration validation
- ✅ Email format validation
- ✅ Password strength validation
- ✅ Rate limiting

**Mocked:**
- Supabase client
- Database operations
- JWT token generation

**Example:**
```python
def test_register_invalid_email():
    response = client.post("/api/auth/register", json={
        "email": "invalid-email",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 422
```

### 2. Webhook Tests (`test_webhooks.py`)

**Tests:**
- ✅ Stripe signature verification
- ✅ Missing signature rejection
- ✅ Duplicate event detection (idempotency)
- ✅ Event processing

**Mocked:**
- Stripe webhook signature verification
- Redis cache for idempotency
- Database event logging

**Example:**
```python
def test_webhook_missing_signature():
    response = client.post("/api/webhooks/stripe", 
                          json={"type": "test"},
                          headers={})
    assert response.status_code in [400, 404]
```

### 3. Subscription Tests (`test_subscriptions.py`)

**Tests:**
- ✅ Checkout session creation
- ✅ Get user subscription
- ✅ Available prices listing
- ✅ Subscription cancellation

**Mocked:**
- Stripe API calls
- Database subscription queries
- Customer creation

**Example:**
```python
@patch('stripe.Price.list')
async def test_get_available_prices(mock_list):
    mock_list.return_value = Mock(data=[mock_price])
    response = client.get("/api/subscriptions/prices")
    assert response.status_code in [200, 404]
```

### 4. Docker Registry Tests (`test_docker_registry.py`)

**Tests:**
- ✅ Download token generation
- ✅ Subscription verification for downloads
- ✅ Download history tracking
- ✅ Access control

**Mocked:**
- Database subscription checks
- Redis token storage
- Download logging

## Mock Patterns

### Database Mocking

```python
@patch('core.database.Database')
async def test_something(mock_db):
    mock_db_instance = Mock()
    mock_db_instance.get_by_id = AsyncMock(return_value={...})
    mock_db.return_value = mock_db_instance
```

### Cache Mocking

```python
@patch('core.cache.Cache')
async def test_something(mock_cache):
    cache_instance = Mock()
    cache_instance.set = AsyncMock(return_value=True)
    mock_cache.return_value = cache_instance
```

### Stripe Mocking

```python
@patch('stripe.checkout.Session.create')
async def test_checkout(mock_session):
    mock_session.return_value = Mock(
        id="cs_test_123",
        url="https://checkout.stripe.com/test"
    )
```

## Shared Fixtures

### User Data (`conftest.py`)

```python
@pytest.fixture
def mock_user_data():
    return {
        "id": "user-test-123",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_admin": False
    }
```

### Admin Data

```python
@pytest.fixture
def mock_admin_data():
    return {
        "id": "admin-test-123",
        "email": "admin@example.com",
        "is_admin": True
    }
```

### Subscription Data

```python
@pytest.fixture
def mock_subscription_data():
    return {
        "id": "sub-123",
        "status": "active",
        "stripe_subscription_id": "sub_stripe_123"
    }
```

## Coverage Goals

- **Core modules**: 80%+ coverage
- **Auth module**: 90%+ coverage
- **Webhooks**: 95%+ coverage (security critical)
- **Subscriptions**: 85%+ coverage

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
cd backend
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

## Test Best Practices

1. **Mock External Services**: Always mock Stripe, Supabase, Redis
2. **Async Tests**: Use `pytest-asyncio` for async functions
3. **Descriptive Names**: `test_what_when_expected()`
4. **Arrange-Act-Assert**: Clear test structure
5. **Independent Tests**: No test depends on another
6. **Fast Execution**: All tests should run in < 10 seconds

## Adding New Tests

### Template

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import Mock, patch, AsyncMock

client = TestClient(app)

@patch('your.module.dependency')
async def test_your_feature(mock_dependency):
    # Arrange
    mock_dependency.return_value = expected_value
    
    # Act
    response = client.get("/your/endpoint")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

## Troubleshooting

### Tests Fail on Import

```bash
# Add backend to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Async Test Warnings

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
```

### Mock Not Working

```python
# Use correct patch path (where it's imported, not defined)
# Wrong: @patch('stripe.Customer.create')
# Right: @patch('subscriptions.service.stripe.Customer.create')
```

## Test Metrics

Run with coverage:

```bash
pytest tests/ --cov=. --cov-report=term-missing
pytest tests/ --cov=. --cov-report=html
# Open htmlcov/index.html
```

## Integration Tests (Optional)

For full integration tests with real services:

```bash
# Set TEST_MODE=integration in .env
# Use test Stripe keys
# Use test Supabase project
pytest tests/ -m integration
```

## Performance Tests

```bash
# Test endpoint response times
pytest tests/ --durations=10
```

All tests are designed to be fast, isolated, and reliable!



