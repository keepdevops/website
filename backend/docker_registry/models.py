from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DockerImage(BaseModel):
    id: str
    name: str
    tag: str
    registry_url: str
    size_mb: Optional[float] = None
    created_at: datetime
    product_id: Optional[str] = None

class DownloadToken(BaseModel):
    token: str
    image_name: str
    expires_at: datetime
    download_url: str

class DownloadRequest(BaseModel):
    image_name: str
    tag: str = "latest"

class DownloadLog(BaseModel):
    id: str
    user_id: str
    image_name: str
    downloaded_at: datetime
    ip_address: Optional[str] = None

class DockerCredentials(BaseModel):
    username: str
    password: str
    registry_url: str

