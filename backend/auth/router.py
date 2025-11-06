from fastapi import APIRouter, Depends, HTTPException, status
from auth.models import UserRegister, UserLogin, TokenResponse, PasswordReset, UserUpdate, TwoFactorLoginVerify
from auth.service import AuthService
from core.database import get_database, Database
from core.cache import get_cache, Cache
from core.dependencies import get_current_user, RateLimiter
from core.event_bus import get_event_bus, EventBus

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

def get_auth_service(
    db: Database = Depends(get_database),
    cache: Cache = Depends(get_cache)
) -> AuthService:
    return AuthService(db, cache)

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service),
    event_bus: EventBus = Depends(get_event_bus)
):
    if not await rate_limiter.check_rate_limit(f"register:{user_data.email}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts"
        )
    
    result = await auth_service.register_user(user_data)
    
    await event_bus.publish("user.registered", {
        "user_id": result.user["id"],
        "email": result.user["email"]
    })
    
    return result

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
    event_bus: EventBus = Depends(get_event_bus)
):
    if not await rate_limiter.check_rate_limit(f"login:{credentials.email}"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts"
        )
    
    result = await auth_service.login_user(credentials)
    
    await event_bus.publish("user.logged_in", {
        "user_id": result.user["id"],
        "email": result.user["email"]
    })
    
    return result

@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
    event_bus: EventBus = Depends(get_event_bus)
):
    result = await auth_service.logout_user(current_user["id"])
    
    await event_bus.publish("user.logged_out", {
        "user_id": current_user["id"]
    })
    
    return result

@router.get("/me")
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=dict)
async def update_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    update_data = user_update.model_dump(exclude_unset=True)
    
    if update_data:
        await db.update_by_id("profiles", current_user["id"], update_data)
    
    updated_user = await db.get_by_id("profiles", current_user["id"])
    return updated_user

@router.post("/password-reset")
async def request_password_reset(
    reset_data: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service)
):
    return {"message": "Password reset email sent"}

@router.get("/verify-token")
async def verify_token(current_user: dict = Depends(get_current_user)):
    return {"valid": True, "user": current_user}

@router.post("/login/2fa", response_model=TokenResponse)
async def verify_2fa_login(
    verify_data: TwoFactorLoginVerify,
    auth_service: AuthService = Depends(get_auth_service),
    db: Database = Depends(get_database),
    cache: Cache = Depends(get_cache)
):
    """Complete login after 2FA verification"""
    # Import here to avoid circular dependency
    from two_factor.service import TwoFactorService
    
    # Check if there's a pending 2FA login
    pending_login = await cache.get_json(f"pending_2fa:{verify_data.user_id}")
    if not pending_login:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending 2FA login found or session expired"
        )
    
    # Verify the 2FA code
    two_factor_service = TwoFactorService(db, cache)
    is_valid = await two_factor_service.verify_totp(verify_data.user_id, verify_data.code)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code"
        )
    
    # Complete the login
    return await auth_service.complete_2fa_login(verify_data.user_id)


