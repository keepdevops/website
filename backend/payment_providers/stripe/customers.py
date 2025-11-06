import stripe
from typing import Optional, Dict, Any
from core.database import Database
import logging

logger = logging.getLogger(__name__)


class StripeCustomerService:
    """Handles Stripe customer creation and management"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def get_or_create_customer(
        self,
        user_id: str,
        email: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get existing Stripe customer or create new one.
        
        Args:
            user_id: Internal user ID
            email: User email
            metadata: Optional metadata to attach to customer
        
        Returns:
            Stripe customer ID
        """
        # Check if user already has a Stripe customer
        existing = await self.db.get_by_id("profiles", user_id)
        
        if existing and existing.get("stripe_customer_id"):
            return existing["stripe_customer_id"]
        
        # Create new Stripe customer
        return await self.create_customer(user_id, email, metadata)
    
    async def create_customer(
        self,
        user_id: str,
        email: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new Stripe customer.
        
        Args:
            user_id: Internal user ID
            email: User email
            metadata: Optional metadata
        
        Returns:
            Stripe customer ID
        """
        customer_metadata = metadata or {}
        customer_metadata["user_id"] = user_id
        
        customer = stripe.Customer.create(
            email=email,
            metadata=customer_metadata
        )
        
        # Update profile with Stripe customer ID
        await self.db.update_by_id("profiles", user_id, {
            "stripe_customer_id": customer.id
        })
        
        logger.info(f"Created Stripe customer {customer.id} for user {user_id}")
        return customer.id
    
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve Stripe customer details.
        
        Args:
            customer_id: Stripe customer ID
        
        Returns:
            Customer object or None
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return {
                "id": customer.id,
                "email": customer.email,
                "metadata": customer.metadata
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving customer {customer_id}: {str(e)}")
            return None


