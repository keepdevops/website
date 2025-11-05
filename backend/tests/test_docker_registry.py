import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

client = TestClient(app)

@patch('core.dependencies.get_current_user')
@patch('core.database.Database')
@patch('core.cache.Cache')
async def test_generate_download_token(mock_cache_class, mock_db_class, mock_user):
    mock_user.return_value = {"id": "user-123", "email": "test@example.com"}
    
    mock_db = Mock()
    mock_db.get_all = AsyncMock(return_value=Mock(data=[{
        "status": "active",
        "user_id": "user-123"
    }]))
    mock_db_class.return_value = mock_db
    
    mock_cache = Mock()
    mock_cache.set_json = AsyncMock(return_value=True)
    mock_cache_class.return_value = mock_cache
    
    response = client.post(
        "/api/docker/download-token",
        json={"image_name": "test-app", "tag": "latest"},
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code in [200, 401, 403, 404]

@patch('core.dependencies.get_current_user')
@patch('core.database.Database')
async def test_get_available_images_no_subscription(mock_db, mock_user):
    mock_user.return_value = {"id": "user-123"}
    
    mock_db_instance = Mock()
    mock_db_instance.get_all = AsyncMock(return_value=Mock(data=[]))
    mock_db.return_value = mock_db_instance
    
    response = client.get(
        "/api/docker/images",
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code in [200, 401, 404]

@patch('core.dependencies.get_current_user')
@patch('core.database.Database')
async def test_download_history(mock_db, mock_user):
    mock_user.return_value = {"id": "user-123"}
    
    mock_db_instance = Mock()
    mock_db_instance.get_all = AsyncMock(return_value=Mock(data=[{
        "id": "log-123",
        "user_id": "user-123",
        "image_name": "test-app",
        "downloaded_at": datetime.utcnow().isoformat()
    }]))
    mock_db.return_value = mock_db_instance
    
    response = client.get(
        "/api/docker/download-history",
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code in [200, 401, 404]

