"""
AWS SNS SMS provider implementation.
Serverless SMS delivery integrated with AWS ecosystem.
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
from datetime import datetime
from core.sms_interface import SMSProviderInterface


class AWSSNSSMSProvider(SMSProviderInterface):
    """AWS SNS SMS provider"""
    
    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        region: str = "us-east-1"
    ):
        self.sns_client = boto3.client(
            'sns',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
        self.verification_codes: Dict[str, str] = {}
    
    async def send_sms(
        self,
        to: str,
        message: str,
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send SMS via AWS SNS"""
        try:
            response = self.sns_client.publish(
                PhoneNumber=to,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )
            
            return {
                "message_id": response['MessageId'],
                "status": "sent",
                "to": to,
                "from": "AWS SNS",
                "cost": None,  # AWS SNS doesn't return cost directly
                "sent_at": datetime.utcnow().isoformat()
            }
        except ClientError as e:
            raise Exception(f"AWS SNS SMS send failed: {str(e)}")
    
    async def send_verification_code(
        self,
        to: str,
        code: str,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send verification code"""
        message = template or f"Your verification code is: {code}"
        self.verification_codes[to] = code
        return await self.send_sms(to, message)
    
    async def verify_phone(
        self,
        phone: str,
        code: str
    ) -> bool:
        """Verify phone number"""
        stored_code = self.verification_codes.get(phone)
        
        if stored_code and stored_code == code:
            del self.verification_codes[phone]
            return True
        
        return False
    
    async def get_message_status(
        self,
        message_id: str
    ) -> Dict[str, Any]:
        """Get message status (AWS SNS doesn't provide detailed tracking)"""
        return {
            "message_id": message_id,
            "status": "unknown",
            "note": "AWS SNS does not provide message delivery status tracking"
        }

