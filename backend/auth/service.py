from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from config import settings
from core.database import get_supabase_client, Database
from core.cache import Cache
from auth.models import UserRegister, UserLogin, TokenResponse
import logging

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Database, cache: Cache):
        self.db = db
        self.cache = cache
        self.supabase = get_supabase_client()
    
    def create_access_token(self, user_id: str, email: str) -> str:
        expires_delta = timedelta(minutes=settings.jwt_expiration_minutes)
        expire = datetime.utcnow() + expires_delta
        
        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    
    async def register_user(self, user_data: UserRegister) -> TokenResponse:
        try:
            auth_response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password
            })
            
            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed"
                )
            
            profile_data = {
                "id": auth_response.user.id,
                "email": user_data.email,
                "full_name": user_data.full_name,
                "is_admin": False,
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.db.create("profiles", profile_data)
            
            access_token = self.create_access_token(
                auth_response.user.id,
                user_data.email
            )
            
            return TokenResponse(
                access_token=access_token,
                user={
                    "id": auth_response.user.id,
                    "email": user_data.email,
                    "full_name": user_data.full_name
                }
            )
        
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def login_user(self, credentials: UserLogin) -> TokenResponse:
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password
            })
            
            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            profile = await self.db.get_by_id("profiles", auth_response.user.id)
            
            if not profile:
                profile = {
                    "id": auth_response.user.id,
                    "email": credentials.email,
                    "full_name": credentials.email.split("@")[0]
                }
            
            # Check if user has 2FA enabled
            if profile.get("two_factor_enabled"):
                # Store pending login in cache for 2FA verification
                await self.cache.set_json(
                    f"pending_2fa:{auth_response.user.id}",
                    {
                        "user_id": auth_response.user.id,
                        "email": credentials.email,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    expiration=300  # 5 minutes
                )
                
                # Return response indicating 2FA is required
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="2FA verification required",
                    headers={"X-Requires-2FA": "true", "X-User-ID": auth_response.user.id}
                )
            
            access_token = self.create_access_token(
                auth_response.user.id,
                credentials.email
            )
            
            return TokenResponse(
                access_token=access_token,
                user=profile
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    
    async def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except Exception:
            return None
    
    async def logout_user(self, user_id: str):
        await self.cache.delete(f"user_session:{user_id}")
        return {"message": "Logged out successfully"}
    
    async def complete_2fa_login(self, user_id: str) -> TokenResponse:
        """Complete login after successful 2FA verification"""
        profile = await self.db.get_by_id("profiles", user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Clear pending 2FA login
        await self.cache.delete(f"pending_2fa:{user_id}")
        
        access_token = self.create_access_token(
            user_id,
            profile["email"]
        )
        
        return TokenResponse(
            access_token=access_token,
            user=profile
        )


