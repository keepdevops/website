from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AnalyticsEvent:
    """Analytics event structure"""
    event_name: str
    user_id: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class AnalyticsProviderInterface(ABC):
    """Abstract interface for analytics providers (GA4, Mixpanel, PostHog, etc.)"""
    
    @abstractmethod
    async def track_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track a custom event.
        
        Args:
            event_name: Name of the event (e.g., 'user_signup', 'purchase_completed')
            user_id: Optional user identifier
            properties: Event properties/metadata
        
        Returns:
            True if tracked successfully
        """
        pass
    
    @abstractmethod
    async def track_page_view(
        self,
        user_id: Optional[str],
        page: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track a page view.
        
        Args:
            user_id: User identifier (can be None for anonymous)
            page: Page path or name
            properties: Additional properties (referrer, campaign, etc.)
        
        Returns:
            True if tracked successfully
        """
        pass
    
    @abstractmethod
    async def identify_user(
        self,
        user_id: str,
        traits: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Identify a user with traits.
        
        Args:
            user_id: User identifier
            traits: User attributes (email, name, plan, etc.)
        
        Returns:
            True if identified successfully
        """
        pass
    
    @abstractmethod
    async def track_revenue(
        self,
        user_id: str,
        amount: float,
        currency: str = "usd",
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track revenue/purchase.
        
        Args:
            user_id: User identifier
            amount: Revenue amount
            currency: Currency code (default: usd)
            properties: Transaction properties
        
        Returns:
            True if tracked successfully
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this analytics provider"""
        pass

