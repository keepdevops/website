from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from campaigns.models import CampaignCreate, CampaignUpdate, Campaign, CampaignList
from campaigns.service import CampaignService
from core.database import get_database, Database
from core.dependencies import get_current_admin_user
from utils.email import get_email_service, EmailService

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])

def get_campaign_service(
    db: Database = Depends(get_database),
    email_service: EmailService = Depends(get_email_service)
) -> CampaignService:
    return CampaignService(db, email_service)

@router.post("/", response_model=Campaign, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: dict = Depends(get_current_admin_user),
    campaign_service: CampaignService = Depends(get_campaign_service)
):
    return await campaign_service.create_campaign(campaign_data)

@router.get("/", response_model=CampaignList)
async def list_campaigns(
    current_user: dict = Depends(get_current_admin_user),
    campaign_service: CampaignService = Depends(get_campaign_service)
):
    return await campaign_service.list_campaigns()

@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_admin_user),
    campaign_service: CampaignService = Depends(get_campaign_service)
):
    campaign = await campaign_service.get_campaign(campaign_id)
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign

@router.put("/{campaign_id}", response_model=Campaign)
async def update_campaign(
    campaign_id: str,
    update_data: CampaignUpdate,
    current_user: dict = Depends(get_current_admin_user),
    campaign_service: CampaignService = Depends(get_campaign_service)
):
    return await campaign_service.update_campaign(campaign_id, update_data)

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_admin_user),
    campaign_service: CampaignService = Depends(get_campaign_service)
):
    return await campaign_service.delete_campaign(campaign_id)

@router.post("/{campaign_id}/send")
async def send_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_admin_user),
    campaign_service: CampaignService = Depends(get_campaign_service)
):
    return await campaign_service.send_campaign(campaign_id)



