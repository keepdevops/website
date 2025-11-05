import stripe
from fastapi import HTTPException, status, Request
from config import settings
from core.cache import Cache
import logging

logger = logging.getLogger(__name__)

class WebhookValidator:
    def __init__(self, cache: Cache):
        self.cache = cache
        self.webhook_secret = settings.stripe_webhook_secret
    
    async def verify_stripe_signature(self, request: Request) -> dict:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing stripe-signature header"
            )
        
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                self.webhook_secret
            )
            return event
        
        except ValueError:
            logger.error("Invalid payload")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payload"
            )
        
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid signature"
            )
    
    async def check_idempotency(self, event_id: str) -> bool:
        key = f"webhook_event:{event_id}"
        
        if await self.cache.exists(key):
            logger.warning(f"Duplicate webhook event: {event_id}")
            return False
        
        await self.cache.set(key, "processed", expiration=86400)
        return True
    
    async def validate_event(self, event: dict) -> bool:
        if not event.get("id"):
            return False
        
        if not event.get("type"):
            return False
        
        if not await self.check_idempotency(event["id"]):
            return False
        
        return True
    
    def validate_request_size(self, request: Request) -> bool:
        content_length = request.headers.get("content-length")
        
        if content_length:
            if int(content_length) > 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Request too large"
                )
        
        return True

