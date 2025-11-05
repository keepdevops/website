from datetime import datetime
from core.database import Database
from core.event_bus import EventBus
import logging

logger = logging.getLogger(__name__)

class PaymentWebhookHandler:
    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
    
    async def handle_payment_succeeded(self, event: dict):
        payment_intent = event["data"]["object"]
        customer_id = payment_intent.get("customer")
        
        if not customer_id:
            logger.warning("Payment intent has no customer")
            return
        
        profile = await self._get_profile_by_stripe_customer(customer_id)
        if not profile:
            logger.error(f"Profile not found for customer: {customer_id}")
            return
        
        await self.event_bus.publish("payment.succeeded", {
            "user_id": profile["id"],
            "payment_intent_id": payment_intent["id"],
            "amount": payment_intent["amount"],
            "currency": payment_intent["currency"]
        })
        
        logger.info(f"Payment succeeded for user: {profile['id']}")
    
    async def handle_payment_failed(self, event: dict):
        payment_intent = event["data"]["object"]
        customer_id = payment_intent.get("customer")
        
        if not customer_id:
            return
        
        profile = await self._get_profile_by_stripe_customer(customer_id)
        if not profile:
            return
        
        await self.event_bus.publish("payment.failed", {
            "user_id": profile["id"],
            "payment_intent_id": payment_intent["id"],
            "error": payment_intent.get("last_payment_error", {}).get("message")
        })
        
        logger.warning(f"Payment failed for user: {profile['id']}")
    
    async def handle_payment_action_required(self, event: dict):
        payment_intent = event["data"]["object"]
        customer_id = payment_intent.get("customer")
        
        if not customer_id:
            return
        
        profile = await self._get_profile_by_stripe_customer(customer_id)
        if not profile:
            return
        
        await self.event_bus.publish("payment.action_required", {
            "user_id": profile["id"],
            "payment_intent_id": payment_intent["id"],
            "client_secret": payment_intent["client_secret"]
        })
        
        logger.info(f"Payment action required for user: {profile['id']}")
    
    async def _get_profile_by_stripe_customer(self, customer_id: str):
        result = await self.db.get_all("profiles", {"stripe_customer_id": customer_id}, limit=1)
        return result.data[0] if result.data else None

