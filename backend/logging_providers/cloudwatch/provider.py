"""
AWS CloudWatch logging provider implementation.
AWS-native logging with CloudWatch Logs integration.
"""
import boto3
from botocore.exceptions import ClientError
import traceback
import json
from typing import Optional, Dict, Any
from datetime import datetime
from core.logging_interface import LoggingProviderInterface


class CloudWatchLoggingProvider(LoggingProviderInterface):
    """AWS CloudWatch Logs provider"""
    
    def __init__(
        self,
        log_group: str = "/aws/saas-app",
        log_stream: str = "backend",
        region: str = "us-east-1"
    ):
        self.client = boto3.client('logs', region_name=region)
        self.log_group = log_group
        self.log_stream = log_stream
        self.sequence_token = None
        self._ensure_log_stream()
    
    def _ensure_log_stream(self):
        """Create log group and stream if they don't exist"""
        try:
            self.client.create_log_group(logGroupName=self.log_group)
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                print(f"Error creating log group: {e}")
        
        try:
            self.client.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                print(f"Error creating log stream: {e}")
    
    async def _send_log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None
    ) -> None:
        """Send log to CloudWatch"""
        log_data = {
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_data["context"] = context
        
        if error:
            log_data["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "stack": ''.join(traceback.format_exception(
                    type(error), error, error.__traceback__
                ))
            }
        
        log_event = {
            "timestamp": int(datetime.utcnow().timestamp() * 1000),
            "message": json.dumps(log_data)
        }
        
        try:
            params = {
                "logGroupName": self.log_group,
                "logStreamName": self.log_stream,
                "logEvents": [log_event]
            }
            
            if self.sequence_token:
                params["sequenceToken"] = self.sequence_token
            
            response = self.client.put_log_events(**params)
            self.sequence_token = response.get('nextSequenceToken')
        except ClientError as e:
            print(f"CloudWatch logging failed: {e}")
    
    async def log_info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log info to CloudWatch"""
        await self._send_log("INFO", message, context)
    
    async def log_warning(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log warning to CloudWatch"""
        await self._send_log("WARNING", message, context)
    
    async def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log error to CloudWatch"""
        await self._send_log("ERROR", message, context, error)
    
    async def log_debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log debug to CloudWatch"""
        await self._send_log("DEBUG", message, context)

