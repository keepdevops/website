"""
Better Stack logging provider implementation.
Modern, developer-friendly log management platform.
"""
import httpx
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
from core.logging_interface import LoggingProviderInterface


class BetterStackLoggingProvider(LoggingProviderInterface):
    """Better Stack (Logtail) logging provider"""
    
    def __init__(self, source_token: str):
        self.source_token = source_token
        self.api_url = "https://in.logs.betterstack.com"
    
    async def _send_log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> None:
        """Send log to Better Stack"""
        log_entry = {
            "dt": datetime.utcnow().isoformat(),
            "level": level,
            "message": message
        }
        
        if context:
            log_entry["context"] = context
        
        if error:
            log_entry["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "stack": ''.join(traceback.format_exception(
                    type(error), error, error.__traceback__
                ))
            }
        
        headers = {
            "Authorization": f"Bearer {self.source_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    self.api_url,
                    json=log_entry,
                    headers=headers,
                    timeout=5.0
                )
            except Exception as e:
                print(f"Better Stack logging failed: {e}, message: {message}")
    
    async def log_info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log info to Better Stack"""
        await self._send_log("info", message, context)
    
    async def log_warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log warning to Better Stack"""
        await self._send_log("warn", message, context)
    
    async def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error to Better Stack"""
        await self._send_log("error", message, context, error)
    
    async def log_debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log debug to Better Stack"""
        await self._send_log("debug", message, context)

