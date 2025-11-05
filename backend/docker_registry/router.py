from fastapi import APIRouter, Depends, Request
from typing import List
from docker_registry.models import DockerImage, DownloadToken, DownloadRequest, DownloadLog
from docker_registry.service import DockerRegistryService
from core.database import get_database, Database
from core.cache import get_cache, Cache
from core.dependencies import get_current_user
from core.event_bus import get_event_bus, EventBus

router = APIRouter(prefix="/api/docker", tags=["Docker Registry"])

def get_docker_service(
    db: Database = Depends(get_database),
    cache: Cache = Depends(get_cache)
) -> DockerRegistryService:
    return DockerRegistryService(db, cache)

@router.get("/images", response_model=List[DockerImage])
async def list_available_images(
    current_user: dict = Depends(get_current_user),
    docker_service: DockerRegistryService = Depends(get_docker_service)
):
    return await docker_service.get_available_images(current_user["id"])

@router.post("/download-token", response_model=DownloadToken)
async def create_download_token(
    download_request: DownloadRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
    docker_service: DockerRegistryService = Depends(get_docker_service),
    event_bus: EventBus = Depends(get_event_bus)
):
    token = await docker_service.generate_download_token(current_user["id"], download_request)
    
    ip_address = request.client.host if request.client else None
    await docker_service.record_download(current_user["id"], download_request.image_name, ip_address)
    
    await event_bus.publish("docker.download_requested", {
        "user_id": current_user["id"],
        "image_name": download_request.image_name
    })
    
    return token

@router.get("/download-history")
async def get_download_history(
    current_user: dict = Depends(get_current_user),
    docker_service: DockerRegistryService = Depends(get_docker_service)
):
    history = await docker_service.get_user_download_history(current_user["id"])
    return {"downloads": history}

@router.get("/credentials")
async def get_docker_credentials(
    current_user: dict = Depends(get_current_user),
    docker_service: DockerRegistryService = Depends(get_docker_service)
):
    return {
        "registry_url": docker_service.registry_url,
        "instructions": "Use the download token as your password"
    }

