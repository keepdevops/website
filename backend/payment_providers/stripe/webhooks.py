import stripe
from typing import Dict, Any
from fastapi import Request, HTTPException, status
import logging

logger = logging.getLogger(__name__)


class StripeWebhookService:
    """Handles Stripe webhook signature verification"""
    
    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret
    
    async def verify_webhook(
        self,
        request: Request,
        signature_header: str = None
    ) -> Dict[str, Any]:
        """
        Verify Stripe webhook signature and return event data.
        
        Args:
            request: FastAPI request object
            signature_header: Stripe signature header (if not in request)
        
        Returns:
            {
                "type": str,  # Event type
                "data": dict  # Event data
            }
        
        Raises:
            HTTPException: If signature verification fails
        """
        # Get signature from header
        sig_header = signature_header or request.headers.get("stripe-signature")
        
        if not sig_header:
            logger.error("Missing stripe-signature header")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing stripe-signature header"
            )
        
        # Get raw body
        try:
            payload = await request.body()
            
            # Verify signature
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                self.webhook_secret
            )
            
            logger.info(f"Webhook verified: {event['type']}")
            
            return {
                "type": event["type"],
                "data": event["data"]["object"]
            }
        
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload"
            )
        
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
    
    def parse_webhook_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse webhook event into standardized format.
        
        Args:
            event_data: Raw event data from Stripe
        
        Returns:
            Standardized event data
        """
        event_type = event_data.get("type", "")
        data_object = event_data.get("data", {}).get("object", {})
        
        # Extract common fields
        parsed = {
            "event_type": event_type,
            "event_id": event_data.get("id"),
            "created": event_data.get("created"),
            "object_id": data_object.get("id"),
            "object_type": data_object.get("object"),
            "customer_id": data_object.get("customer"),
            "raw_data": data_object
        }
        
        return parsed


