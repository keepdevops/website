from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from jose import JWTError, jwt
from config import settings
from core.database import get_database, Database
from core.cache import get_cache, Cache
from core.event_bus import get_event_bus, EventBus

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Database = Depends(get_database)
):
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = await db.get_by_id("profiles", user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_db() -> Database:
    return get_database()

def get_cache_dependency() -> Cache:
    return get_cache()

def get_event_bus_dependency() -> EventBus:
    return get_event_bus()

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.cache = get_cache()
    
    async def check_rate_limit(self, identifier: str) -> bool:
        key = f"rate_limit:{identifier}"
        current = await self.cache.get(key)
        
        if current is None:
            await self.cache.set(key, "1", self.window_seconds)
            return True
        
        count = int(current)
        if count >= self.max_requests:
            return False
        
        await self.cache.increment(key)
        return True



