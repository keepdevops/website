from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class ErrorSeverity(Enum):
    """Error severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """Context information for error logging"""
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class MonitoringProviderInterface(ABC):
    """Abstract interface for monitoring/error tracking providers"""
    
    @abstractmethod
    async def log_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> bool:
        """
        Log an error/exception.
        
        Args:
            error: Exception object
            context: Additional context (user, request, etc.)
            severity: Error severity level
        
        Returns:
            True if logged successfully
        """
        pass
    
    @abstractmethod
    async def log_message(
        self,
        message: str,
        level: ErrorSeverity = ErrorSeverity.INFO,
        extra: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log a message.
        
        Args:
            message: Log message
            level: Log level
            extra: Extra metadata
        
        Returns:
            True if logged successfully
        """
        pass
    
    @abstractmethod
    async def log_event(
        self,
        event_name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log a custom event.
        
        Args:
            event_name: Name of event
            properties: Event properties
        
        Returns:
            True if logged successfully
        """
        pass
    
    @abstractmethod
    async def set_user_context(
        self,
        user_id: str,
        user_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Set user context for subsequent logs.
        
        Args:
            user_id: User identifier
            user_data: Additional user data (email, name, etc.)
        
        Returns:
            True if context was set
        """
        pass
    
    @abstractmethod
    async def track_performance(
        self,
        operation: str,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track performance metrics.
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            metadata: Additional metadata
        
        Returns:
            True if tracked successfully
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this monitoring provider"""
        pass

