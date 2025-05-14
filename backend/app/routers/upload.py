from fastapi import APIRouter, File, UploadFile
from typing import List
from app.services.upload_service import upload_files_service
from app.models.upload_models import UploadSuccess

router = APIRouter()


@router.post("/upload", response_model=UploadSuccess)
async def upload_files(files: List[UploadFile] = File(...)):
    return await upload_files_service(files)
