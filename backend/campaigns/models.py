from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from datetime import datetime

class CampaignCreate(BaseModel):
    name: str
    subject: str
    content: str
    segment: Optional[str] = "all"
    status: Literal["draft", "scheduled", "sent"] = "draft"
    scheduled_at: Optional[datetime] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None

class Campaign(BaseModel):
    id: str
    name: str
    subject: str
    content: str
    segment: str
    status: str
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    total_recipients: int = 0
    opened_count: int = 0
    clicked_count: int = 0

class CampaignList(BaseModel):
    campaigns: List[Campaign]
    total: int

class EmailTemplate(BaseModel):
    id: str
    name: str
    subject: str
    content: str
    created_at: datetime

