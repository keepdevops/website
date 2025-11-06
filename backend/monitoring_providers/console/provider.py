from typing import Dict, Any, Optional
from core.monitoring_interface import (
    MonitoringProviderInterface,
    ErrorContext,
    ErrorSeverity
)
import logging
import traceback

logger = logging.getLogger(__name__)


class ConsoleMonitoringProvider(MonitoringProviderInterface):
    """Console/logging monitoring provider for development"""
    
    def __init__(self):
        # Configure logging format
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @property
    def provider_name(self) -> str:
        return "console"
    
    def _get_logger_level(self, severity: ErrorSeverity) -> int:
        """Convert ErrorSeverity to logging level"""
        mapping = {
            ErrorSeverity.DEBUG: logging.DEBUG,
            ErrorSeverity.INFO: logging.INFO,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        return mapping.get(severity, logging.ERROR)
    
    async def log_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> bool:
        """Log error to console"""
        try:
            level = self._get_logger_level(severity)
            
            error_msg = f"Error: {str(error)}"
            
            if context:
                context_parts = []
                if context.user_id:
                    context_parts.append(f"User: {context.user_id}")
                if context.request_id:
                    context_parts.append(f"Request: {context.request_id}")
                if context.endpoint:
                    context_parts.append(f"Endpoint: {context.endpoint}")
                
                if context_parts:
                    error_msg += f" | {' | '.join(context_parts)}"
            
            logger.log(level, error_msg)
            logger.log(level, traceback.format_exc())
            
            return True
        
        except Exception as e:
            print(f"Console logging failed: {str(e)}")
            return False
    
    async def log_message(
        self,
        message: str,
        level: ErrorSeverity = ErrorSeverity.INFO,
        extra: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log message to console"""
        try:
            log_level = self._get_logger_level(level)
            
            if extra:
                extra_str = " | ".join([f"{k}={v}" for k, v in extra.items()])
                message = f"{message} | {extra_str}"
            
            logger.log(log_level, message)
            return True
        
        except Exception as e:
            print(f"Console logging failed: {str(e)}")
            return False
    
    async def log_event(
        self,
        event_name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log custom event to console"""
        try:
            event_msg = f"Event: {event_name}"
            
            if properties:
                props_str = " | ".join([f"{k}={v}" for k, v in properties.items()])
                event_msg += f" | {props_str}"
            
            logger.info(event_msg)
            return True
        
        except Exception as e:
            print(f"Console event logging failed: {str(e)}")
            return False
    
    async def set_user_context(
        self,
        user_id: str,
        user_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Set user context (no-op for console, just log it)"""
        logger.info(f"User context set: {user_id}")
        return True
    
    async def track_performance(
        self,
        operation: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track performance to console"""
        try:
            perf_msg = f"Performance: {operation} took {duration_ms:.2f}ms"
            
            if metadata:
                meta_str = " | ".join([f"{k}={v}" for k, v in metadata.items()])
                perf_msg += f" | {meta_str}"
            
            logger.info(perf_msg)
            return True
        
        except Exception as e:
            print(f"Console performance tracking failed: {str(e)}")
            return False

