from typing import Dict, Any, Optional
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from core.monitoring_interface import (
    MonitoringProviderInterface,
    ErrorContext,
    ErrorSeverity
)
import logging

logger = logging.getLogger(__name__)


class SentryMonitoringProvider(MonitoringProviderInterface):
    """Sentry error tracking and performance monitoring"""
    
    def __init__(
        self,
        dsn: str,
        environment: str = "production",
        traces_sample_rate: float = 0.1,
        profiles_sample_rate: float = 0.1
    ):
        self.dsn = dsn
        self.environment = environment
        
        # Initialize Sentry
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            integrations=[
                FastApiIntegration(),
                RedisIntegration()
            ]
        )
        
        logger.info(f"Sentry initialized for environment: {environment}")
    
    @property
    def provider_name(self) -> str:
        return "sentry"
    
    def _severity_to_level(self, severity: ErrorSeverity) -> str:
        """Convert ErrorSeverity to Sentry level"""
        mapping = {
            ErrorSeverity.DEBUG: "debug",
            ErrorSeverity.INFO: "info",
            ErrorSeverity.WARNING: "warning",
            ErrorSeverity.ERROR: "error",
            ErrorSeverity.CRITICAL: "fatal"
        }
        return mapping.get(severity, "error")
    
    async def log_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> bool:
        """Log error to Sentry"""
        try:
            # Set context if provided
            if context:
                with sentry_sdk.push_scope() as scope:
                    if context.user_id:
                        scope.set_user({"id": context.user_id})
                    
                    if context.request_id:
                        scope.set_tag("request_id", context.request_id)
                    
                    if context.endpoint:
                        scope.set_tag("endpoint", context.endpoint)
                    
                    if context.extra_data:
                        for key, value in context.extra_data.items():
                            scope.set_extra(key, value)
                    
                    scope.level = self._severity_to_level(severity)
                    sentry_sdk.capture_exception(error)
            else:
                sentry_sdk.capture_exception(error)
            
            return True
        
        except Exception as e:
            logger.error(f"Sentry error logging failed: {str(e)}")
            return False
    
    async def log_message(
        self,
        message: str,
        level: ErrorSeverity = ErrorSeverity.INFO,
        extra: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log message to Sentry"""
        try:
            sentry_level = self._severity_to_level(level)
            
            if extra:
                with sentry_sdk.push_scope() as scope:
                    for key, value in extra.items():
                        scope.set_extra(key, value)
                    sentry_sdk.capture_message(message, level=sentry_level)
            else:
                sentry_sdk.capture_message(message, level=sentry_level)
            
            return True
        
        except Exception as e:
            logger.error(f"Sentry message logging failed: {str(e)}")
            return False
    
    async def log_event(
        self,
        event_name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log custom event to Sentry"""
        try:
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("event_name", event_name)
                if properties:
                    for key, value in properties.items():
                        scope.set_extra(key, value)
                
                sentry_sdk.capture_message(f"Event: {event_name}", level="info")
            
            return True
        
        except Exception as e:
            logger.error(f"Sentry event logging failed: {str(e)}")
            return False
    
    async def set_user_context(
        self,
        user_id: str,
        user_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Set user context in Sentry"""
        try:
            user_info = {"id": user_id}
            if user_data:
                user_info.update(user_data)
            
            sentry_sdk.set_user(user_info)
            return True
        
        except Exception as e:
            logger.error(f"Sentry set user context failed: {str(e)}")
            return False
    
    async def track_performance(
        self,
        operation: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track performance in Sentry"""
        try:
            with sentry_sdk.start_transaction(op=operation, name=operation) as transaction:
                transaction.set_measurement("duration", duration_ms, "millisecond")
                
                if metadata:
                    for key, value in metadata.items():
                        transaction.set_data(key, value)
            
            return True
        
        except Exception as e:
            logger.error(f"Sentry performance tracking failed: {str(e)}")
            return False

