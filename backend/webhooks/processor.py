from typing import Callable, Dict
import logging
from core.event_bus import EventBus
from core.database import Database

logger = logging.getLogger(__name__)

class WebhookProcessor:
    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        self.handlers[event_type] = handler
        logger.info(f"Registered webhook handler for: {event_type}")
    
    async def process_event(self, event: dict):
        event_type = event.get("type")
        
        if not event_type:
            logger.error("Event type missing")
            return
        
        await self._log_event(event)
        
        handler = self.handlers.get(event_type)
        
        if handler:
            try:
                await handler(event)
                logger.info(f"Successfully processed event: {event_type}")
            except Exception as e:
                logger.error(f"Error processing event {event_type}: {str(e)}")
                await self._log_error(event, str(e))
        else:
            logger.warning(f"No handler for event type: {event_type}")
    
    async def _log_event(self, event: dict):
        try:
            await self.db.create("webhook_events", {
                "event_id": event["id"],
                "event_type": event["type"],
                "data": event,
                "processed": False,
                "created_at": event.get("created")
            })
        except Exception as e:
            logger.error(f"Error logging webhook event: {str(e)}")
    
    async def _log_error(self, event: dict, error_message: str):
        try:
            await self.db.execute_query(
                "webhook_events",
                "update",
                data={"error": error_message, "processed": False},
                match_column="event_id",
                match_value=event["id"]
            )
        except Exception as e:
            logger.error(f"Error logging webhook error: {str(e)}")
    
    async def mark_event_processed(self, event_id: str):
        try:
            await self.db.execute_query(
                "webhook_events",
                "update",
                data={"processed": True},
                match_column="event_id",
                match_value=event_id
            )
        except Exception as e:
            logger.error(f"Error marking event as processed: {str(e)}")
    
    async def dispatch_to_event_bus(self, event_type: str, data: dict):
        await self.event_bus.publish(f"stripe.{event_type}", data)

