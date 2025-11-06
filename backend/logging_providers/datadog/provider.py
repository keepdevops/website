"""
Datadog logging provider implementation.
Enterprise observability platform with full-stack monitoring.
"""
import httpx
import traceback
from typing import Optional, Dict, Any
from datetime import datetime
from core.logging_interface import LoggingProviderInterface


class DatadogLoggingProvider(LoggingProviderInterface):
    """Datadog logging provider"""
    
    def __init__(
        self,
        api_key: str,
        app_key: Optional[str] = None,
        site: str = "datadoghq.com"
    ):
        self.api_key = api_key
        self.app_key = app_key
        self.site = site
        self.api_url = f"https://http-intake.logs.{site}/api/v2/logs"
        self.service_name = "saas-backend"
    
    async def _send_log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> None:
        """Send log to Datadog"""
        log_entry = {
            "ddsource": "python",
            "ddtags": f"env:production,service:{self.service_name}",
            "hostname": "backend-server",
            "message": message,
            "level": level,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_entry.update(context)
        
        if error:
            log_entry["error"] = {
                "kind": type(error).__name__,
                "message": str(error),
                "stack": ''.join(traceback.format_exception(
                    type(error), error, error.__traceback__
                ))
            }
        
        headers = {
            "DD-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    self.api_url,
                    json=[log_entry],
                    headers=headers,
                    timeout=5.0
                )
            except Exception as e:
                # Fallback to console if Datadog fails
                print(f"Datadog logging failed: {e}, message: {message}")
    
    async def log_info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log info to Datadog"""
        await self._send_log("info", message, context)
    
    async def log_warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log warning to Datadog"""
        await self._send_log("warn", message, context)
    
    async def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error to Datadog"""
        await self._send_log("error", message, context, error)
    
    async def log_debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log debug to Datadog"""
        await self._send_log("debug", message, context)

