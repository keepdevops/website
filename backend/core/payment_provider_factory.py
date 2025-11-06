from typing import Optional
from core.payment_interface import PaymentProviderInterface
from core.database import Database
from config import settings
import logging

logger = logging.getLogger(__name__)


# Singleton instance
_provider_instance: Optional[PaymentProviderInterface] = None


def get_payment_provider(db: Database) -> PaymentProviderInterface:
    """
    Get payment provider instance based on configuration.
    
    Args:
        db: Database instance
    
    Returns:
        PaymentProviderInterface implementation
    
    Raises:
        ValueError: If provider not configured or unknown
    """
    global _provider_instance
    
    provider_name = getattr(settings, 'payment_provider', 'stripe')
    
    if provider_name == "stripe":
        from payment_providers.stripe import StripePaymentProvider
        return StripePaymentProvider(db)
    
    elif provider_name == "paypal":
        from payment_providers.paypal.provider import PayPalPaymentProvider
        return PayPalPaymentProvider(
            client_id=settings.paypal_client_id,
            client_secret=settings.paypal_client_secret,
            mode=settings.paypal_mode
        )
    
    elif provider_name == "square":
        from payment_providers.square.provider import SquarePaymentProvider
        return SquarePaymentProvider(
            access_token=settings.square_access_token,
            environment=settings.square_environment
        )
    
    elif provider_name == "braintree":
        from payment_providers.braintree.provider import BraintreePaymentProvider
        return BraintreePaymentProvider(
            merchant_id=settings.braintree_merchant_id,
            public_key=settings.braintree_public_key,
            private_key=settings.braintree_private_key,
            environment=settings.braintree_environment
        )
    
    elif provider_name == "adyen":
        from payment_providers.adyen.provider import AdyenPaymentProvider
        return AdyenPaymentProvider(
            api_key=settings.adyen_api_key,
            merchant_account=settings.adyen_merchant_account,
            environment=settings.adyen_environment
        )
    
    raise ValueError(f"Unknown payment provider: {provider_name}")


def get_payment_provider_by_name(
    provider_name: str,
    db: Database
) -> PaymentProviderInterface:
    """
    Get a specific payment provider by name.
    
    Useful for webhook endpoints that need to handle multiple providers.
    
    Args:
        provider_name: Name of provider (e.g., 'stripe', 'paypal')
        db: Database instance
    
    Returns:
        PaymentProviderInterface implementation
    
    Raises:
        ValueError: If provider unknown
    """
    if provider_name == "stripe":
        from payment_providers.stripe import StripePaymentProvider
        return StripePaymentProvider(db)
    
    elif provider_name == "paypal":
        from payment_providers.paypal.provider import PayPalPaymentProvider
        return PayPalPaymentProvider(
            client_id=settings.paypal_client_id,
            client_secret=settings.paypal_client_secret,
            mode=settings.paypal_mode
        )
    
    elif provider_name == "square":
        from payment_providers.square.provider import SquarePaymentProvider
        return SquarePaymentProvider(
            access_token=settings.square_access_token,
            environment=settings.square_environment
        )
    
    elif provider_name == "braintree":
        from payment_providers.braintree.provider import BraintreePaymentProvider
        return BraintreePaymentProvider(
            merchant_id=settings.braintree_merchant_id,
            public_key=settings.braintree_public_key,
            private_key=settings.braintree_private_key,
            environment=settings.braintree_environment
        )
    
    elif provider_name == "adyen":
        from payment_providers.adyen.provider import AdyenPaymentProvider
        return AdyenPaymentProvider(
            api_key=settings.adyen_api_key,
            merchant_account=settings.adyen_merchant_account,
            environment=settings.adyen_environment
        )
    
    raise ValueError(f"Unknown payment provider: {provider_name}")


