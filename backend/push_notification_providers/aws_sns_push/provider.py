"""
AWS SNS Push notification provider implementation.
AWS-native mobile push notifications for iOS and Android.
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, List, Dict, Any
import json
from core.push_notification_interface import PushNotificationInterface


class AWSSNSPushProvider(PushNotificationInterface):
    """AWS SNS Push notification provider"""
    
    def __init__(
        self,
        platform_application_arn: str,
        region: str = "us-east-1"
    ):
        self.sns_client = boto3.client('sns', region_name=region)
        self.platform_application_arn = platform_application_arn
        self.device_endpoints: Dict[str, str] = {}  # device_token -> endpoint_arn
    
    async def send_notification(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image_url: Optional[str] = None,
        action_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send push notification via AWS SNS"""
        # Create message payload for both iOS and Android
        message_payload = {
            "default": body,
            "APNS": json.dumps({
                "aps": {
                    "alert": {"title": title, "body": body},
                    "sound": "default"
                },
                "data": data or {}
            }),
            "GCM": json.dumps({
                "notification": {"title": title, "body": body},
                "data": data or {}
            })
        }
        
        sent_count = 0
        for endpoint_arn in self.device_endpoints.values():
            try:
                self.sns_client.publish(
                    TargetArn=endpoint_arn,
                    Message=json.dumps(message_payload),
                    MessageStructure='json'
                )
                sent_count += 1
            except ClientError:
                pass
        
        return {
            "notification_id": "sns_push",
            "recipients": sent_count
        }
    
    async def send_to_segment(
        self,
        segment: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send to topic (segment)"""
        topic_arn = f"{self.platform_application_arn}:topic:{segment}"
        
        message_payload = {
            "default": body,
            "APNS": json.dumps({"aps": {"alert": {"title": title, "body": body}}}),
            "GCM": json.dumps({"notification": {"title": title, "body": body}})
        }
        
        try:
            self.sns_client.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message_payload),
                MessageStructure='json'
            )
            return {"notification_id": "sns_topic", "segment": segment}
        except ClientError as e:
            raise Exception(f"SNS topic publish failed: {str(e)}")
    
    async def subscribe_device(
        self,
        user_id: str,
        device_token: str,
        platform: str
    ) -> bool:
        """Register device endpoint"""
        try:
            response = self.sns_client.create_platform_endpoint(
                PlatformApplicationArn=self.platform_application_arn,
                Token=device_token
            )
            self.device_endpoints[device_token] = response['EndpointArn']
            return True
        except ClientError:
            return False
    
    async def unsubscribe_device(self, device_token: str) -> bool:
        """Unregister device endpoint"""
        endpoint_arn = self.device_endpoints.get(device_token)
        if endpoint_arn:
            try:
                self.sns_client.delete_endpoint(EndpointArn=endpoint_arn)
                del self.device_endpoints[device_token]
                return True
            except ClientError:
                return False
        return False
    
    async def get_notification_status(
        self,
        notification_id: str
    ) -> Dict[str, Any]:
        """SNS doesn't provide detailed tracking"""
        return {
            "notification_id": notification_id,
            "status": "unknown",
            "note": "AWS SNS does not provide delivery status tracking"
        }

