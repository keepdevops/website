import stripe
from config import settings
import logging

logger = logging.getLogger(__name__)


def initialize_stripe():
    """Initialize Stripe with API key from settings"""
    stripe.api_key = settings.stripe_secret_key
    logger.info("Stripe API initialized")


def get_stripe_config():
    """Get Stripe configuration"""
    return {
        "secret_key": settings.stripe_secret_key,
        "webhook_secret": settings.stripe_webhook_secret,
        "publishable_key": settings.stripe_publishable_key
    }


# Initialize on module import
initialize_stripe()


