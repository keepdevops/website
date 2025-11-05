import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import Mock, patch, AsyncMock

client = TestClient(app)

@pytest.fixture
def mock_supabase():
    with patch('auth.service.get_supabase_client') as mock:
        mock_client = Mock()
        mock_client.auth.sign_up = Mock(return_value=Mock(
            user=Mock(id="test-user-123", email="test@example.com")
        ))
        mock_client.auth.sign_in_with_password = Mock(return_value=Mock(
            user=Mock(id="test-user-123", email="test@example.com")
        ))
        mock.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_db():
    with patch('core.database.Database') as mock:
        db_instance = Mock()
        db_instance.create = AsyncMock(return_value=Mock(data=[{
            "id": "test-user-123",
            "email": "test@example.com",
            "full_name": "Test User"
        }]))
        db_instance.get_by_id = AsyncMock(return_value={
            "id": "test-user-123",
            "email": "test@example.com",
            "full_name": "Test User"
        })
        mock.return_value = db_instance
        yield db_instance

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

@patch('auth.service.get_supabase_client')
@patch('core.database.Database')
async def test_register_user(mock_db_class, mock_supabase_func):
    mock_supabase = Mock()
    mock_supabase.auth.sign_up.return_value = Mock(
        user=Mock(id="user-123", email="new@test.com")
    )
    mock_supabase_func.return_value = mock_supabase
    
    mock_db = Mock()
    mock_db.create = AsyncMock()
    mock_db_class.return_value = mock_db
    
    response = client.post("/api/auth/register", json={
        "email": "new@test.com",
        "password": "password123",
        "full_name": "New User"
    })
    
    assert response.status_code in [200, 201, 429]

def test_register_invalid_email():
    response = client.post("/api/auth/register", json={
        "email": "invalid-email",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 422

def test_register_short_password():
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "short",
        "full_name": "Test User"
    })
    assert response.status_code == 422

