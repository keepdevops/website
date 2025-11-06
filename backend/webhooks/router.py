from fastapi import APIRouter, Depends, Request, BackgroundTasks, HTTPException, status
from webhooks.validator import WebhookValidator
from webhooks.processor import WebhookProcessor
from webhooks.handlers.subscription import SubscriptionWebhookHandler
from webhooks.handlers.payment import PaymentWebhookHandler
from webhooks.handlers.invoice import InvoiceWebhookHandler
from core.database import get_database, Database
from core.cache import get_cache, Cache
from core.event_bus import get_event_bus, EventBus
from core.payment_provider_factory import get_payment_provider_by_name
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

def get_webhook_validator(cache: Cache = Depends(get_cache)) -> WebhookValidator:
    return WebhookValidator(cache)

def get_webhook_processor(
    db: Database = Depends(get_database),
    event_bus: EventBus = Depends(get_event_bus)
) -> WebhookProcessor:
    processor = WebhookProcessor(db, event_bus)
    
    sub_handler = SubscriptionWebhookHandler(db, event_bus)
    payment_handler = PaymentWebhookHandler(db, event_bus)
    invoice_handler = InvoiceWebhookHandler(db, event_bus)
    
    processor.register_handler("customer.subscription.created", sub_handler.handle_subscription_created)
    processor.register_handler("customer.subscription.updated", sub_handler.handle_subscription_updated)
    processor.register_handler("customer.subscription.deleted", sub_handler.handle_subscription_deleted)
    
    processor.register_handler("payment_intent.succeeded", payment_handler.handle_payment_succeeded)
    processor.register_handler("payment_intent.payment_failed", payment_handler.handle_payment_failed)
    processor.register_handler("payment_intent.requires_action", payment_handler.handle_payment_action_required)
    
    processor.register_handler("invoice.paid", invoice_handler.handle_invoice_paid)
    processor.register_handler("invoice.payment_failed", invoice_handler.handle_invoice_payment_failed)
    processor.register_handler("invoice.upcoming", invoice_handler.handle_invoice_upcoming)
    
    return processor

@router.post("/{provider}")
async def handle_webhook(
    provider: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Database = Depends(get_database),
    cache: Cache = Depends(get_cache),
    processor: WebhookProcessor = Depends(get_webhook_processor)
):
    """
    Handle webhook from payment provider.
    
    Provider-agnostic endpoint that delegates to the appropriate payment provider.
    URL pattern: /api/webhooks/{provider} (e.g., /api/webhooks/stripe)
    """
    try:
        # Get provider-specific implementation
        payment_provider = get_payment_provider_by_name(provider, db)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown payment provider: {provider}"
        )
    
    # Validate request size
    validator = WebhookValidator(cache)
    validator.validate_request_size(request)
    
    # Verify webhook signature using provider
    event = await payment_provider.verify_webhook(request)
    
    # Validate event (check for duplicates)
    if not await validator.validate_event(event):
        logger.info(f"Duplicate {provider} webhook event: {event.get('type')}")
        return {"status": "duplicate"}
    
    # Process event in background
    background_tasks.add_task(processor.process_event, event)
    
    logger.info(f"Accepted {provider} webhook: {event.get('type')}")
    return {"status": "received"}


# Legacy Stripe endpoint for backward compatibility
@router.post("/stripe")
async def handle_stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Database = Depends(get_database),
    cache: Cache = Depends(get_cache),
    processor: WebhookProcessor = Depends(get_webhook_processor)
):
    """Legacy Stripe webhook endpoint (redirects to new provider-agnostic endpoint)"""
    return await handle_webhook("stripe", request, background_tasks, db, cache, processor)


