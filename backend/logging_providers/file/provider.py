"""
File logging provider implementation.
Rotating file logs with size-based rotation.
"""
import logging
from logging.handlers import RotatingFileHandler
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
from core.logging_interface import LoggingProviderInterface


class FileLoggingProvider(LoggingProviderInterface):
    """File-based logging with rotation"""
    
    def __init__(
        self,
        log_file_path: str = "logs/app.log",
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5
    ):
        self.log_file_path = log_file_path
        self.logger = self._setup_logger(max_bytes, backup_count)
    
    def _setup_logger(self, max_bytes: int, backup_count: int) -> logging.Logger:
        """Setup rotating file logger"""
        import os
        
        # Create log directory
        log_dir = os.path.dirname(self.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Create logger
        logger = logging.getLogger('saas_app')
        logger.setLevel(logging.DEBUG)
        
        # Create rotating file handler
        handler = RotatingFileHandler(
            self.log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def _format_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format message with context"""
        if context:
            context_str = " | " + ", ".join(f"{k}={v}" for k, v in context.items())
            return message + context_str
        return message
    
    async def log_info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log info to file"""
        self.logger.info(self._format_message(message, context))
    
    async def log_warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log warning to file"""
        self.logger.warning(self._format_message(message, context))
    
    async def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error to file with stack trace"""
        formatted_message = self._format_message(message, context)
        
        if error:
            formatted_message += f"\nException: {type(error).__name__}: {str(error)}"
            formatted_message += f"\nStack trace:\n{''.join(traceback.format_exception(type(error), error, error.__traceback__))}"
        
        self.logger.error(formatted_message)
    
    async def log_debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log debug to file"""
        self.logger.debug(self._format_message(message, context))

