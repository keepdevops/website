from datetime import datetime
from core.database import Database
from core.event_bus import EventBus
import logging

logger = logging.getLogger(__name__)

class SubscriptionWebhookHandler:
    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
    
    async def handle_subscription_created(self, event: dict):
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        
        profile = await self._get_profile_by_stripe_customer(customer_id)
        if not profile:
            logger.error(f"Profile not found for customer: {customer_id}")
            return
        
        sub_data = {
            "user_id": profile["id"],
            "stripe_customer_id": customer_id,
            "stripe_subscription_id": subscription["id"],
            "status": subscription["status"],
            "current_period_start": datetime.fromtimestamp(
                subscription["current_period_start"]
            ).isoformat(),
            "current_period_end": datetime.fromtimestamp(
                subscription["current_period_end"]
            ).isoformat(),
            "cancel_at_period_end": subscription["cancel_at_period_end"],
            "created_at": datetime.utcnow().isoformat()
        }
        
        await self.db.create("subscriptions", sub_data)
        
        await self.event_bus.publish("subscription.created", {
            "user_id": profile["id"],
            "subscription_id": subscription["id"]
        })
        
        logger.info(f"Subscription created for user: {profile['id']}")
    
    async def handle_subscription_updated(self, event: dict):
        subscription = event["data"]["object"]
        
        existing = await self._get_subscription_by_stripe_id(subscription["id"])
        if not existing:
            await self.handle_subscription_created(event)
            return
        
        update_data = {
            "status": subscription["status"],
            "current_period_end": datetime.fromtimestamp(
                subscription["current_period_end"]
            ).isoformat(),
            "cancel_at_period_end": subscription["cancel_at_period_end"],
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await self.db.update_by_id("subscriptions", existing["id"], update_data)
        
        await self.event_bus.publish("subscription.updated", {
            "user_id": existing["user_id"],
            "subscription_id": subscription["id"],
            "status": subscription["status"]
        })
        
        logger.info(f"Subscription updated: {subscription['id']}")
    
    async def handle_subscription_deleted(self, event: dict):
        subscription = event["data"]["object"]
        
        existing = await self._get_subscription_by_stripe_id(subscription["id"])
        if not existing:
            logger.warning(f"Subscription not found: {subscription['id']}")
            return
        
        await self.db.update_by_id("subscriptions", existing["id"], {
            "status": "canceled",
            "updated_at": datetime.utcnow().isoformat()
        })
        
        await self.event_bus.publish("subscription.deleted", {
            "user_id": existing["user_id"],
            "subscription_id": subscription["id"]
        })
        
        logger.info(f"Subscription deleted: {subscription['id']}")
    
    async def _get_profile_by_stripe_customer(self, customer_id: str):
        result = await self.db.get_all("profiles", {"stripe_customer_id": customer_id}, limit=1)
        return result.data[0] if result.data else None
    
    async def _get_subscription_by_stripe_id(self, subscription_id: str):
        result = await self.db.get_all(
            "subscriptions",
            {"stripe_subscription_id": subscription_id},
            limit=1
        )
        return result.data[0] if result.data else None



