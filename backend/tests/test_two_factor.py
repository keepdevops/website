import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from two_factor.service import TwoFactorService
from core.database import Database
from core.cache import Cache


@pytest.fixture
def mock_db():
    """Mock database"""
    db = AsyncMock(spec=Database)
    return db


@pytest.fixture
def mock_cache():
    """Mock cache"""
    cache = AsyncMock(spec=Cache)
    return cache


@pytest.fixture
def two_factor_service(mock_db, mock_cache):
    """Create TwoFactorService instance with mocked dependencies"""
    return TwoFactorService(mock_db, mock_cache)


class TestTwoFactorService:
    
    @pytest.mark.asyncio
    async def test_setup_totp(self, two_factor_service, mock_cache):
        """Test setting up TOTP 2FA"""
        user_id = "test-user-id"
        email = "test@example.com"
        
        result = await two_factor_service.setup_totp(user_id, email)
        
        assert result.secret is not None
        assert result.qr_code_url.startswith("data:image/png;base64,")
        assert len(result.backup_codes) == 8
        
        # Verify cache was called to store setup data
        mock_cache.set_json.assert_called_once()
        call_args = mock_cache.set_json.call_args
        assert call_args[0][0] == f"2fa_setup:{user_id}"
        assert "secret" in call_args[0][1]
        assert "backup_codes" in call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_enable_2fa_success(self, two_factor_service, mock_cache, mock_db):
        """Test successfully enabling 2FA with valid code"""
        user_id = "test-user-id"
        
        # Mock setup data in cache
        mock_cache.get_json.return_value = {
            "secret": "JBSWY3DPEHPK3PXP",
            "backup_codes": ["AAAA-BBBB-CCCC", "DDDD-EEEE-FFFF"]
        }
        
        with patch('pyotp.TOTP') as mock_totp:
            mock_totp_instance = MagicMock()
            mock_totp_instance.verify.return_value = True
            mock_totp.return_value = mock_totp_instance
            
            result = await two_factor_service.enable_2fa(user_id, "123456")
            
            assert result is True
            mock_db.update_by_id.assert_called_once()
            mock_cache.delete.assert_called_once_with(f"2fa_setup:{user_id}")
    
    @pytest.mark.asyncio
    async def test_enable_2fa_invalid_code(self, two_factor_service, mock_cache):
        """Test enabling 2FA with invalid code"""
        user_id = "test-user-id"
        
        mock_cache.get_json.return_value = {
            "secret": "JBSWY3DPEHPK3PXP",
            "backup_codes": ["AAAA-BBBB-CCCC"]
        }
        
        with patch('pyotp.TOTP') as mock_totp:
            mock_totp_instance = MagicMock()
            mock_totp_instance.verify.return_value = False
            mock_totp.return_value = mock_totp_instance
            
            with pytest.raises(ValueError, match="Invalid verification code"):
                await two_factor_service.enable_2fa(user_id, "999999")
    
    @pytest.mark.asyncio
    async def test_enable_2fa_no_setup(self, two_factor_service, mock_cache):
        """Test enabling 2FA without setup"""
        user_id = "test-user-id"
        mock_cache.get_json.return_value = None
        
        with pytest.raises(ValueError, match="No 2FA setup in progress"):
            await two_factor_service.enable_2fa(user_id, "123456")
    
    @pytest.mark.asyncio
    async def test_verify_totp_success(self, two_factor_service, mock_db):
        """Test successful TOTP verification"""
        user_id = "test-user-id"
        
        mock_db.get_by_id.return_value = {
            "id": user_id,
            "two_factor_enabled": True,
            "two_factor_secret": "JBSWY3DPEHPK3PXP"
        }
        
        with patch('pyotp.TOTP') as mock_totp:
            mock_totp_instance = MagicMock()
            mock_totp_instance.verify.return_value = True
            mock_totp.return_value = mock_totp_instance
            
            result = await two_factor_service.verify_totp(user_id, "123456")
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_totp_not_enabled(self, two_factor_service, mock_db):
        """Test verifying TOTP when 2FA is not enabled"""
        user_id = "test-user-id"
        
        mock_db.get_by_id.return_value = {
            "id": user_id,
            "two_factor_enabled": False
        }
        
        result = await two_factor_service.verify_totp(user_id, "123456")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_verify_backup_code_success(self, two_factor_service, mock_db):
        """Test successful backup code verification"""
        user_id = "test-user-id"
        backup_code = "AAAA-BBBB-CCCC"
        
        # Hash the backup code
        import hashlib
        code_hash = hashlib.sha256(backup_code.encode()).hexdigest()
        
        mock_db.get_by_id.return_value = {
            "id": user_id,
            "two_factor_enabled": True,
            "backup_codes": [code_hash, "other_hash"]
        }
        
        result = await two_factor_service.verify_backup_code(user_id, backup_code)
        
        assert result is True
        # Verify the used code was removed
        mock_db.update_by_id.assert_called_once()
        update_call = mock_db.update_by_id.call_args
        assert len(update_call[0][2]["backup_codes"]) == 1
    
    @pytest.mark.asyncio
    async def test_verify_backup_code_invalid(self, two_factor_service, mock_db):
        """Test verifying invalid backup code"""
        user_id = "test-user-id"
        
        mock_db.get_by_id.return_value = {
            "id": user_id,
            "two_factor_enabled": True,
            "backup_codes": ["some_hash"]
        }
        
        result = await two_factor_service.verify_backup_code(user_id, "WRONG-CODE-XXXX")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_disable_2fa(self, two_factor_service, mock_db):
        """Test disabling 2FA"""
        user_id = "test-user-id"
        
        result = await two_factor_service.disable_2fa(user_id)
        
        assert result is True
        mock_db.update_by_id.assert_called_once()
        update_call = mock_db.update_by_id.call_args
        assert update_call[0][2]["two_factor_enabled"] is False
        assert update_call[0][2]["two_factor_secret"] is None
    
    @pytest.mark.asyncio
    async def test_get_2fa_status(self, two_factor_service, mock_db):
        """Test getting 2FA status"""
        user_id = "test-user-id"
        
        mock_db.get_by_id.return_value = {
            "two_factor_enabled": True,
            "two_factor_method": "totp",
            "backup_codes": ["hash1", "hash2", "hash3"]
        }
        
        status = await two_factor_service.get_2fa_status(user_id)
        
        assert status.enabled is True
        assert status.method == "totp"
        assert status.backup_codes_remaining == 3
    
    def test_generate_backup_codes(self, two_factor_service):
        """Test backup code generation"""
        codes = two_factor_service._generate_backup_codes(count=5)
        
        assert len(codes) == 5
        for code in codes:
            # Format: XXXX-XXXX-XXXX
            assert len(code.split('-')) == 3
            assert all(len(part) == 4 for part in code.split('-'))
    
    def test_hash_backup_code(self, two_factor_service):
        """Test backup code hashing"""
        code = "TEST-CODE-1234"
        hashed = two_factor_service._hash_backup_code(code)
        
        # SHA256 hash should be 64 characters
        assert len(hashed) == 64
        
        # Same code should produce same hash
        hashed2 = two_factor_service._hash_backup_code(code)
        assert hashed == hashed2


