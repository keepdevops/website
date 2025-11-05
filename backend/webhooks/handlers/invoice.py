from datetime import datetime
from core.database import Database
from core.event_bus import EventBus
import logging

logger = logging.getLogger(__name__)

class InvoiceWebhookHandler:
    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
    
    async def handle_invoice_paid(self, event: dict):
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        
        if not customer_id:
            return
        
        profile = await self._get_profile_by_stripe_customer(customer_id)
        if not profile:
            logger.error(f"Profile not found for customer: {customer_id}")
            return
        
        await self.event_bus.publish("invoice.paid", {
            "user_id": profile["id"],
            "invoice_id": invoice["id"],
            "amount_paid": invoice["amount_paid"],
            "currency": invoice["currency"],
            "period_start": invoice["period_start"],
            "period_end": invoice["period_end"]
        })
        
        logger.info(f"Invoice paid for user: {profile['id']}")
    
    async def handle_invoice_payment_failed(self, event: dict):
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        
        if not customer_id:
            return
        
        profile = await self._get_profile_by_stripe_customer(customer_id)
        if not profile:
            return
        
        await self.event_bus.publish("invoice.payment_failed", {
            "user_id": profile["id"],
            "invoice_id": invoice["id"],
            "amount_due": invoice["amount_due"],
            "attempt_count": invoice["attempt_count"]
        })
        
        logger.warning(f"Invoice payment failed for user: {profile['id']}")
    
    async def handle_invoice_upcoming(self, event: dict):
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        
        if not customer_id:
            return
        
        profile = await self._get_profile_by_stripe_customer(customer_id)
        if not profile:
            return
        
        await self.event_bus.publish("invoice.upcoming", {
            "user_id": profile["id"],
            "amount_due": invoice["amount_due"],
            "next_payment_attempt": invoice.get("next_payment_attempt")
        })
        
        logger.info(f"Upcoming invoice for user: {profile['id']}")
    
    async def _get_profile_by_stripe_customer(self, customer_id: str):
        result = await self.db.get_all("profiles", {"stripe_customer_id": customer_id}, limit=1)
        return result.data[0] if result.data else None

