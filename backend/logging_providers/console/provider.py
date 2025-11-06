"""
Console logging provider implementation.
Simple stdout logging for development and debugging.
"""
import sys
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
from core.logging_interface import LoggingProviderInterface


class ConsoleLoggingProvider(LoggingProviderInterface):
    """Console logging provider for development"""
    
    def __init__(self, colorize: bool = True):
        self.colorize = colorize
        self.colors = {
            'debug': '\033[36m',     # Cyan
            'info': '\033[32m',      # Green
            'warning': '\033[33m',   # Yellow
            'error': '\033[31m',     # Red
            'reset': '\033[0m'
        }
    
    def _format_log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Format log message"""
        timestamp = datetime.utcnow().isoformat()
        color_start = self.colors.get(level, '') if self.colorize else ''
        color_end = self.colors['reset'] if self.colorize else ''
        
        log_line = f"{color_start}[{timestamp}] {level.upper()}: {message}{color_end}"
        
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            log_line += f" | {context_str}"
        
        return log_line
    
    async def log_info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log info to console"""
        print(self._format_log('info', message, context), file=sys.stdout)
    
    async def log_warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log warning to console"""
        print(self._format_log('warning', message, context), file=sys.stderr)
    
    async def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error to console with stack trace"""
        log_line = self._format_log('error', message, context)
        print(log_line, file=sys.stderr)
        
        if error:
            print(f"  Exception: {type(error).__name__}: {str(error)}", file=sys.stderr)
            print(f"  Stack trace:", file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    
    async def log_debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log debug to console"""
        print(self._format_log('debug', message, context), file=sys.stdout)

