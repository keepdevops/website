from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, List
import time
import uuid
from core.monitoring_interface import MonitoringProviderInterface, ErrorContext, ErrorSeverity
from core.monitoring_factory import get_monitoring_providers
import logging

logger = logging.getLogger(__name__)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to integrate monitoring providers with FastAPI"""
    
    def __init__(self, app, providers: List[MonitoringProviderInterface] = None):
        super().__init__(app)
        self.providers = providers or get_monitoring_providers()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and track to monitoring providers"""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Set request context
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Track performance
            duration_ms = (time.time() - start_time) * 1000
            
            # Log to all providers
            for provider in self.providers:
                try:
                    await provider.track_performance(
                        operation=f"{request.method} {request.url.path}",
                        duration_ms=duration_ms,
                        metadata={
                            "status_code": response.status_code,
                            "request_id": request_id,
                            "method": request.method,
                            "path": request.url.path
                        }
                    )
                except Exception as e:
                    logger.error(f"Monitoring provider {provider.provider_name} failed: {str(e)}")
            
            return response
        
        except Exception as error:
            # Log error to all providers
            context = ErrorContext(
                request_id=request_id,
                endpoint=f"{request.method} {request.url.path}",
                extra_data={
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params)
                }
            )
            
            for provider in self.providers:
                try:
                    await provider.log_error(error, context, ErrorSeverity.ERROR)
                except Exception as e:
                    logger.error(f"Monitoring provider {provider.provider_name} failed: {str(e)}")
            
            # Re-raise the error for FastAPI to handle
            raise


class MonitoringService:
    """High-level monitoring service for manual logging"""
    
    def __init__(self, providers: List[MonitoringProviderInterface] = None):
        self.providers = providers or get_monitoring_providers()
    
    async def log_error(self, error: Exception, context: Optional[ErrorContext] = None):
        """Log error to all monitoring providers"""
        for provider in self.providers:
            try:
                await provider.log_error(error, context)
            except Exception as e:
                logger.error(f"Provider {provider.provider_name} failed: {str(e)}")
    
    async def log_event(self, event_name: str, properties: Optional[dict] = None):
        """Log event to all monitoring providers"""
        for provider in self.providers:
            try:
                await provider.log_event(event_name, properties)
            except Exception as e:
                logger.error(f"Provider {provider.provider_name} failed: {str(e)}")


def get_monitoring_service() -> MonitoringService:
    """Get MonitoringService instance"""
    return MonitoringService()

