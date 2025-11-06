import pyotp
import qrcode
import io
import base64
import secrets
from typing import Optional, List
from datetime import datetime
from core.database import Database
from core.cache import Cache
from two_factor.models import TwoFactorSetupResponse, TwoFactorStatus
import logging

logger = logging.getLogger(__name__)

class TwoFactorService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db
        self.cache = cache
    
    async def setup_totp(self, user_id: str, user_email: str) -> TwoFactorSetupResponse:
        secret = pyotp.random_base32()
        
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name="SaaS Platform"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_code_url = f"data:image/png;base64,{qr_code_base64}"
        
        backup_codes = self._generate_backup_codes()
        
        await self.cache.set_json(f"2fa_setup:{user_id}", {
            "secret": secret,
            "backup_codes": backup_codes,
            "created_at": datetime.utcnow().isoformat()
        }, expiration=900)
        
        return TwoFactorSetupResponse(
            secret=secret,
            qr_code_url=qr_code_url,
            backup_codes=backup_codes
        )
    
    def _generate_backup_codes(self, count: int = 8) -> List[str]:
        codes = []
        for _ in range(count):
            code = '-'.join([
                secrets.token_hex(2).upper(),
                secrets.token_hex(2).upper(),
                secrets.token_hex(2).upper()
            ])
            codes.append(code)
        return codes
    
    async def enable_2fa(self, user_id: str, code: str) -> bool:
        setup_data = await self.cache.get_json(f"2fa_setup:{user_id}")
        
        if not setup_data:
            raise ValueError("No 2FA setup in progress")
        
        secret = setup_data["secret"]
        totp = pyotp.TOTP(secret)
        
        if not totp.verify(code, valid_window=1):
            raise ValueError("Invalid verification code")
        
        backup_codes_hashed = [
            self._hash_backup_code(bc) for bc in setup_data["backup_codes"]
        ]
        
        await self.db.update_by_id("profiles", user_id, {
            "two_factor_enabled": True,
            "two_factor_secret": secret,
            "two_factor_method": "totp",
            "backup_codes": backup_codes_hashed,
            "two_factor_enabled_at": datetime.utcnow().isoformat()
        })
        
        await self.cache.delete(f"2fa_setup:{user_id}")
        
        logger.info(f"2FA enabled for user: {user_id}")
        return True
    
    async def verify_totp(self, user_id: str, code: str) -> bool:
        user = await self.db.get_by_id("profiles", user_id)
        
        if not user or not user.get("two_factor_enabled"):
            return False
        
        secret = user.get("two_factor_secret")
        if not secret:
            return False
        
        totp = pyotp.TOTP(secret)
        is_valid = totp.verify(code, valid_window=1)
        
        if is_valid:
            await self._log_2fa_verification(user_id, "totp", True)
        
        return is_valid
    
    async def verify_backup_code(self, user_id: str, backup_code: str) -> bool:
        user = await self.db.get_by_id("profiles", user_id)
        
        if not user or not user.get("two_factor_enabled"):
            return False
        
        backup_codes = user.get("backup_codes", [])
        code_hash = self._hash_backup_code(backup_code)
        
        if code_hash not in backup_codes:
            return False
        
        backup_codes.remove(code_hash)
        
        await self.db.update_by_id("profiles", user_id, {
            "backup_codes": backup_codes
        })
        
        await self._log_2fa_verification(user_id, "backup_code", True)
        
        logger.info(f"Backup code used for user: {user_id}, {len(backup_codes)} remaining")
        return True
    
    async def disable_2fa(self, user_id: str) -> bool:
        await self.db.update_by_id("profiles", user_id, {
            "two_factor_enabled": False,
            "two_factor_secret": None,
            "two_factor_method": None,
            "backup_codes": []
        })
        
        logger.info(f"2FA disabled for user: {user_id}")
        return True
    
    async def get_2fa_status(self, user_id: str) -> TwoFactorStatus:
        user = await self.db.get_by_id("profiles", user_id)
        
        return TwoFactorStatus(
            enabled=user.get("two_factor_enabled", False),
            method=user.get("two_factor_method"),
            backup_codes_remaining=len(user.get("backup_codes", []))
        )
    
    def _hash_backup_code(self, code: str) -> str:
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()
    
    async def _log_2fa_verification(self, user_id: str, method: str, success: bool):
        try:
            await self.db.create("two_factor_logs", {
                "user_id": user_id,
                "method": method,
                "success": success,
                "verified_at": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Error logging 2FA verification: {str(e)}")



