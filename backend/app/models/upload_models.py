from pydantic import BaseModel
from typing import List, Optional


class UploadResponse(BaseModel):
    stored_filename: str
    preview_url: str
    original_filename: str
    file_size: int
    content_type: Optional[str] = None


class UploadSuccess(BaseModel):
    message: str
    data: List[UploadResponse]
