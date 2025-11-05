from pydantic import BaseModel
from typing import Optional

class TwoFactorSetupRequest(BaseModel):
    method: str = "totp"

class TwoFactorSetupResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: list[str]

class TwoFactorVerifyRequest(BaseModel):
    code: str

class TwoFactorEnableRequest(BaseModel):
    code: str

class TwoFactorDisableRequest(BaseModel):
    password: str
    code: Optional[str] = None

class TwoFactorBackupCodeVerify(BaseModel):
    backup_code: str

class TwoFactorStatus(BaseModel):
    enabled: bool
    method: Optional[str] = None
    backup_codes_remaining: int = 0

