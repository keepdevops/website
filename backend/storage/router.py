"""
Storage API router for file upload/download endpoints.
"""
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel

from storage.service import StorageService
from core.storage_provider_factory import get_storage_provider
from config import settings
from core.dependencies import get_current_user_id


router = APIRouter(prefix="/storage", tags=["storage"])


# Dependency to get storage service
def get_storage_service() -> StorageService:
    """Get configured storage service"""
    provider = get_storage_provider()
    default_bucket = (
        settings.aws_s3_bucket or
        settings.supabase_storage_bucket or
        settings.b2_bucket_name or
        settings.gcs_bucket_name or
        "uploads"
    )
    return StorageService(provider=provider, default_bucket=default_bucket)


class FileUploadResponse(BaseModel):
    """File upload response"""
    url: str
    path: str
    size: int


class FileListItem(BaseModel):
    """File list item"""
    path: str
    size: int
    last_modified: str


@router.post("/upload/avatar", response_model=FileUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    storage: StorageService = Depends(get_storage_service)
):
    """Upload user avatar"""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed for avatars"
            )
        
        # Read file data
        file_data = await file.read()
        
        # Upload avatar
        url = await storage.upload_user_avatar(
            user_id=user_id,
            file_data=file_data,
            filename=file.filename or "avatar.jpg"
        )
        
        return FileUploadResponse(
            url=url,
            path=f"avatars/{user_id}/avatar.jpg",
            size=len(file_data)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.post("/upload/document", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    folder: Optional[str] = "documents",
    user_id: str = Depends(get_current_user_id),
    storage: StorageService = Depends(get_storage_service)
):
    """Upload document file"""
    try:
        # Read file data
        file_data = await file.read()
        
        # Upload document
        result = await storage.upload_document(
            user_id=user_id,
            file_data=file_data,
            filename=file.filename or "document.bin",
            folder=folder
        )
        
        return FileUploadResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/files", response_model=List[FileListItem])
async def list_user_files(
    folder: str = "documents",
    user_id: str = Depends(get_current_user_id),
    storage: StorageService = Depends(get_storage_service)
):
    """List all files for the current user"""
    try:
        files = await storage.list_user_files(user_id=user_id, folder=folder)
        return [FileListItem(**f) for f in files]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"List failed: {str(e)}"
        )


@router.delete("/files/{path:path}")
async def delete_file(
    path: str,
    user_id: str = Depends(get_current_user_id),
    storage: StorageService = Depends(get_storage_service)
):
    """Delete a file (must be owned by current user)"""
    try:
        # Verify file belongs to user
        if not path.startswith(f"documents/{user_id}/") and not path.startswith(f"avatars/{user_id}/"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own files"
            )
        
        success = await storage.delete_file(path=path)
        
        return {"success": success, "path": path}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )

