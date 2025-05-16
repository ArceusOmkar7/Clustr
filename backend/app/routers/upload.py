from fastapi import APIRouter, File, UploadFile, Form, Query
from typing import List, Dict, Any
from app.services.upload_service import upload_files_service
from app.models.upload_models import UploadSuccess, PaginatedUploadsResponse
from app.services.mongodb_service import mongodb_service
from app.utils.image_utils import get_image_dimensions
import os
from app.config import settings

# Create a router for upload-related endpoints
router = APIRouter()


@router.post("/upload", response_model=UploadSuccess)
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload one or more files to the server.

    Parameters:
    - files: A list of files submitted via multipart/form-data. The "..." means this parameter is required.
             FastAPI will automatically handle parsing the uploaded files from the request.

    Returns:
    - UploadSuccess: A model containing a success message and data about each uploaded file.
                    The response is validated against this model before being sent to the client.

    This endpoint delegates the actual file processing to the upload_files_service function,
    keeping the router focused on defining the API structure instead of implementation details.
    """
    return await upload_files_service(files)


@router.get("/uploads", response_model=PaginatedUploadsResponse)
async def get_all_uploads(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    limit: int = Query(
        20, ge=1, le=100, description="Number of items per page, max 100")
):
    """
    Get uploads with pagination.

    Parameters:
    - page: The page number (1-indexed)
    - limit: Number of items per page (max 100)

    Returns:
    - PaginatedUploadsResponse: A model containing paginated upload data
    """
    return mongodb_service.get_paginated_uploads(page, limit)


@router.get("/uploads/{file_id}", response_model=Dict[str, Any])
async def get_upload(file_id: str):
    """
    Get a specific upload by ID.

    Parameters:
    - file_id: The ID of the upload to retrieve

    Returns:
    - Dict: The upload metadata
    """
    metadata = mongodb_service.get_upload_metadata(file_id)
    if metadata is None:
        # If the file doesn't exist, FastAPI will automatically return a 404 response
        return {"error": "File not found"}
    return metadata
