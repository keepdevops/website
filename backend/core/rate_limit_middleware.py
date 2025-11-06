"""
FastAPI middleware for rate limiting.
Applies rate limits to API endpoints based on user/IP.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional
from core.rate_limit_provider_factory import get_rate_limit_provider
from config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to requests"""
    
    def __init__(
        self,
        app,
        default_limit: int = 100,
        default_window: int = 60
    ):
        super().__init__(app)
        self.provider = get_rate_limit_provider()
        self.default_limit = default_limit
        self.default_window = default_window
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Apply rate limiting to request"""
        
        # Skip rate limiting for certain paths
        if self._should_skip(request.url.path):
            return await call_next(request)
        
        # Get rate limit key (prefer user_id, fallback to IP)
        key = await self._get_rate_limit_key(request)
        
        # Get limit and window for this endpoint
        limit, window = self._get_limits(request.url.path)
        
        # Check rate limit
        rate_info = await self.provider.check_rate_limit(key, limit, window)
        
        # Add rate limit headers
        headers = {
            "X-RateLimit-Limit": str(rate_info.limit),
            "X-RateLimit-Remaining": str(rate_info.remaining),
            "X-RateLimit-Reset": str(int(rate_info.reset_at.timestamp()))
        }
        
        if not rate_info.allowed:
            # Rate limit exceeded
            if rate_info.retry_after:
                headers["Retry-After"] = str(rate_info.retry_after)
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": rate_info.retry_after
                },
                headers=headers
            )
        
        # Increment counter
        await self.provider.increment(key, window)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value
        
        return response
    
    def _should_skip(self, path: str) -> bool:
        """Check if path should skip rate limiting"""
        skip_paths = ["/health", "/metrics", "/docs", "/openapi.json"]
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    async def _get_rate_limit_key(self, request: Request) -> str:
        """Get rate limit key from request"""
        # Try to get user_id from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _get_limits(self, path: str) -> tuple[int, int]:
        """Get rate limit and window for path"""
        # Customize limits per endpoint
        if path.startswith("/api/auth/"):
            return 10, 60  # 10 requests per minute for auth endpoints
        elif path.startswith("/api/storage/upload"):
            return 20, 60  # 20 uploads per minute
        else:
            return self.default_limit, self.default_window


def rate_limit(limit: int = 100, window: int = 60):
    """Decorator for applying rate limits to specific endpoints"""
    def decorator(func):
        func._rate_limit = (limit, window)
        return func
    return decorator

