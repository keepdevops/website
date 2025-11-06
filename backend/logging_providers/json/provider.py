"""
JSON logging provider implementation.
Structured JSON logs for log aggregation systems.
"""
import json
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
from core.logging_interface import LoggingProviderInterface


class JSONLoggingProvider(LoggingProviderInterface):
    """JSON structured logging provider"""
    
    def __init__(self, log_file_path: str = "logs/app.json"):
        self.log_file_path = log_file_path
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        import os
        log_dir = os.path.dirname(self.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def _write_log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> None:
        """Write structured JSON log"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level.upper(),
            'message': message
        }
        
        if context:
            log_entry['context'] = context
        
        if error:
            log_entry['error'] = {
                'type': type(error).__name__,
                'message': str(error),
                'traceback': traceback.format_exception(
                    type(error), error, error.__traceback__
                )
            }
        
        with open(self.log_file_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    async def log_info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log info as JSON"""
        self._write_log('info', message, context)
    
    async def log_warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log warning as JSON"""
        self._write_log('warning', message, context)
    
    async def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error as JSON"""
        self._write_log('error', message, context, error)
    
    async def log_debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log debug as JSON"""
        self._write_log('debug', message, context)

