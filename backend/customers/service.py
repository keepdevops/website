from typing import List, Optional
from fastapi import HTTPException, status
from core.database import Database
from customers.models import CustomerProfile, CustomerList, CustomerStats, CustomerSearch
import logging

logger = logging.getLogger(__name__)

class CustomerService:
    def __init__(self, db: Database):
        self.db = db
    
    async def get_customer_by_id(self, customer_id: str) -> Optional[CustomerProfile]:
        customer = await self.db.get_by_id("profiles", customer_id)
        
        if not customer:
            return None
        
        subscription = await self._get_customer_subscription(customer_id)
        
        if subscription:
            customer["subscription_status"] = subscription.get("status")
        
        return CustomerProfile(**customer)
    
    async def get_all_customers(self, search_params: CustomerSearch) -> CustomerList:
        filters = {}
        
        if search_params.is_admin is not None:
            filters["is_admin"] = search_params.is_admin
        
        result = await self.db.get_all("profiles", filters, limit=search_params.page_size)
        
        customers = []
        for customer_data in result.data or []:
            subscription = await self._get_customer_subscription(customer_data["id"])
            
            if subscription:
                customer_data["subscription_status"] = subscription.get("status")
            
            if search_params.subscription_status:
                if customer_data.get("subscription_status") != search_params.subscription_status:
                    continue
            
            customers.append(CustomerProfile(**customer_data))
        
        return CustomerList(
            customers=customers,
            total=len(customers),
            page=search_params.page,
            page_size=search_params.page_size
        )
    
    async def update_customer(self, customer_id: str, update_data: dict) -> CustomerProfile:
        await self.db.update_by_id("profiles", customer_id, update_data)
        return await self.get_customer_by_id(customer_id)
    
    async def delete_customer(self, customer_id: str):
        await self.db.delete_by_id("profiles", customer_id)
        
        subscriptions = await self.db.get_all("subscriptions", {"user_id": customer_id})
        for sub in subscriptions.data or []:
            await self.db.delete_by_id("subscriptions", sub["id"])
        
        return {"message": "Customer deleted successfully"}
    
    async def get_customer_stats(self) -> CustomerStats:
        profiles_result = await self.db.get_all("profiles", limit=10000)
        total_customers = len(profiles_result.data or [])
        
        subscriptions_result = await self.db.get_all("subscriptions", limit=10000)
        subscriptions = subscriptions_result.data or []
        
        active_count = sum(1 for sub in subscriptions if sub.get("status") == "active")
        canceled_count = sum(1 for sub in subscriptions if sub.get("status") == "canceled")
        trial_count = sum(1 for sub in subscriptions if sub.get("status") == "trialing")
        
        return CustomerStats(
            total_customers=total_customers,
            active_subscriptions=active_count,
            canceled_subscriptions=canceled_count,
            trial_subscriptions=trial_count,
            monthly_recurring_revenue=0.0
        )
    
    async def _get_customer_subscription(self, customer_id: str):
        result = await self.db.get_all("subscriptions", {"user_id": customer_id}, limit=1)
        return result.data[0] if result.data else None

