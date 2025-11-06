"""
Abstract interface for logging providers.
Defines operations for structured logging with context.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime


class LoggingProviderInterface(ABC):
    """Abstract interface for logging providers"""
    
    @abstractmethod
    async def log_info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log informational message.
        
        Args:
            message: Log message
            context: Additional context (user_id, request_id, etc.)
        """
        pass
    
    @abstractmethod
    async def log_warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log warning message.
        
        Args:
            message: Warning message
            context: Additional context
        """
        pass
    
    @abstractmethod
    async def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log error message with optional exception.
        
        Args:
            message: Error message
            error: Exception object
            context: Additional context
        """
        pass
    
    @abstractmethod
    async def log_debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log debug message.
        
        Args:
            message: Debug message
            context: Additional context
        """
        pass
    
    async def log_with_level(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> None:
        """
        Log with specific level.
        
        Args:
            level: Log level (debug, info, warning, error)
            message: Log message
            context: Additional context
            error: Optional exception
        """
        level = level.lower()
        if level == "debug":
            await self.log_debug(message, context)
        elif level == "info":
            await self.log_info(message, context)
        elif level == "warning":
            await self.log_warning(message, context)
        elif level == "error":
            await self.log_error(message, error, context)

