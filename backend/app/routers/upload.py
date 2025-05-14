from fastapi import APIRouter, File, UploadFile
from typing import List
from app.services.upload_service import upload_files_service
from app.models.upload_models import UploadSuccess

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
