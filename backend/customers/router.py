from fastapi import APIRouter, Depends, HTTPException, status, Query
from customers.models import CustomerProfile, CustomerList, CustomerStats, CustomerUpdate, CustomerSearch
from customers.service import CustomerService
from core.database import get_database, Database
from core.dependencies import get_current_admin_user
from typing import Optional

router = APIRouter(prefix="/api/customers", tags=["Customers"])

def get_customer_service(db: Database = Depends(get_database)) -> CustomerService:
    return CustomerService(db)

@router.get("/", response_model=CustomerList)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    subscription_status: Optional[str] = None,
    is_admin: Optional[bool] = None,
    current_user: dict = Depends(get_current_admin_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    search_params = CustomerSearch(
        page=page,
        page_size=page_size,
        subscription_status=subscription_status,
        is_admin=is_admin
    )
    return await customer_service.get_all_customers(search_params)

@router.get("/stats", response_model=CustomerStats)
async def get_customer_stats(
    current_user: dict = Depends(get_current_admin_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    return await customer_service.get_customer_stats()

@router.get("/{customer_id}", response_model=CustomerProfile)
async def get_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_admin_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    customer = await customer_service.get_customer_by_id(customer_id)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer

@router.put("/{customer_id}", response_model=CustomerProfile)
async def update_customer(
    customer_id: str,
    update_data: CustomerUpdate,
    current_user: dict = Depends(get_current_admin_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    update_dict = update_data.model_dump(exclude_unset=True)
    return await customer_service.update_customer(customer_id, update_dict)

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_admin_user),
    customer_service: CustomerService = Depends(get_customer_service)
):
    return await customer_service.delete_customer(customer_id)

