from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from core.database import Database
from campaigns.models import CampaignCreate, CampaignUpdate, Campaign, CampaignList
from utils.email import EmailService
import logging

logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self, db: Database, email_service: EmailService):
        self.db = db
        self.email_service = email_service
    
    async def create_campaign(self, campaign_data: CampaignCreate) -> Campaign:
        new_campaign = {
            **campaign_data.model_dump(),
            "created_at": datetime.utcnow().isoformat(),
            "total_recipients": 0,
            "opened_count": 0,
            "clicked_count": 0
        }
        
        result = await self.db.create("campaigns", new_campaign)
        return Campaign(**result.data[0])
    
    async def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        campaign = await self.db.get_by_id("campaigns", campaign_id)
        return Campaign(**campaign) if campaign else None
    
    async def list_campaigns(self, limit: int = 50) -> CampaignList:
        result = await self.db.get_all("campaigns", limit=limit)
        campaigns = [Campaign(**c) for c in result.data or []]
        
        return CampaignList(
            campaigns=campaigns,
            total=len(campaigns)
        )
    
    async def update_campaign(self, campaign_id: str, update_data: CampaignUpdate) -> Campaign:
        update_dict = update_data.model_dump(exclude_unset=True)
        await self.db.update_by_id("campaigns", campaign_id, update_dict)
        return await self.get_campaign(campaign_id)
    
    async def delete_campaign(self, campaign_id: str):
        await self.db.delete_by_id("campaigns", campaign_id)
        return {"message": "Campaign deleted"}
    
    async def send_campaign(self, campaign_id: str) -> dict:
        campaign = await self.get_campaign(campaign_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        recipients = await self._get_campaign_recipients(campaign.segment)
        
        if not recipients:
            return {"message": "No recipients found", "sent": 0}
        
        result = await self.email_service.send_bulk_email(
            recipients=[r["email"] for r in recipients],
            subject=campaign.subject,
            content=campaign.content
        )
        
        await self.db.update_by_id("campaigns", campaign_id, {
            "status": "sent",
            "sent_at": datetime.utcnow().isoformat(),
            "total_recipients": result["sent"]
        })
        
        logger.info(f"Campaign {campaign_id} sent to {result['sent']} recipients")
        
        return result
    
    async def _get_campaign_recipients(self, segment: str) -> List[dict]:
        if segment == "all":
            result = await self.db.get_all("profiles", limit=10000)
            return result.data or []
        
        elif segment == "active_subscribers":
            subscriptions = await self.db.get_all("subscriptions", {"status": "active"}, limit=10000)
            user_ids = [sub["user_id"] for sub in subscriptions.data or []]
            
            recipients = []
            for user_id in user_ids:
                profile = await self.db.get_by_id("profiles", user_id)
                if profile:
                    recipients.append(profile)
            
            return recipients
        
        return []

