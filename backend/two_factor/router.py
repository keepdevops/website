from fastapi import APIRouter, Depends, HTTPException, status
from two_factor.models import (
    TwoFactorSetupResponse, TwoFactorVerifyRequest, TwoFactorEnableRequest,
    TwoFactorDisableRequest, TwoFactorBackupCodeVerify, TwoFactorStatus
)
from two_factor.service import TwoFactorService
from core.database import get_database, Database
from core.cache import get_cache, Cache
from core.dependencies import get_current_user
from core.event_bus import get_event_bus, EventBus

router = APIRouter(prefix="/api/2fa", tags=["Two-Factor Authentication"])

def get_2fa_service(
    db: Database = Depends(get_database),
    cache: Cache = Depends(get_cache)
) -> TwoFactorService:
    return TwoFactorService(db, cache)

@router.post("/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(
    current_user: dict = Depends(get_current_user),
    service: TwoFactorService = Depends(get_2fa_service)
):
    return await service.setup_totp(current_user["id"], current_user["email"])

@router.post("/enable")
async def enable_2fa(
    request: TwoFactorEnableRequest,
    current_user: dict = Depends(get_current_user),
    service: TwoFactorService = Depends(get_2fa_service),
    event_bus: EventBus = Depends(get_event_bus)
):
    try:
        await service.enable_2fa(current_user["id"], request.code)
        
        await event_bus.publish("2fa.enabled", {
            "user_id": current_user["id"]
        })
        
        return {"message": "2FA enabled successfully"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/verify")
async def verify_2fa(
    request: TwoFactorVerifyRequest,
    current_user: dict = Depends(get_current_user),
    service: TwoFactorService = Depends(get_2fa_service)
):
    is_valid = await service.verify_totp(current_user["id"], request.code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code"
        )
    
    return {"verified": True}

@router.post("/verify-backup")
async def verify_backup_code(
    request: TwoFactorBackupCodeVerify,
    current_user: dict = Depends(get_current_user),
    service: TwoFactorService = Depends(get_2fa_service)
):
    is_valid = await service.verify_backup_code(current_user["id"], request.backup_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid backup code"
        )
    
    return {"verified": True}

@router.post("/disable")
async def disable_2fa(
    request: TwoFactorDisableRequest,
    current_user: dict = Depends(get_current_user),
    service: TwoFactorService = Depends(get_2fa_service),
    event_bus: EventBus = Depends(get_event_bus)
):
    await service.disable_2fa(current_user["id"])
    
    await event_bus.publish("2fa.disabled", {
        "user_id": current_user["id"]
    })
    
    return {"message": "2FA disabled successfully"}

@router.get("/status", response_model=TwoFactorStatus)
async def get_2fa_status(
    current_user: dict = Depends(get_current_user),
    service: TwoFactorService = Depends(get_2fa_service)
):
    return await service.get_2fa_status(current_user["id"])

