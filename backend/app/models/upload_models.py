from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class UploadResponse(BaseModel):
    """
    Model representing a single uploaded file in the response.

    This class defines the structure of the data returned for each uploaded file.
    Pydantic ensures the data types are validated and converts data to the right types.
    """
    stored_filename: str     # The filename as stored on the server
    preview_url: str         # Full URL where the uploaded file can be accessed
    original_filename: str   # The original filename from the user's upload
    file_size: int           # Size of the file in bytes
    # MIME type of the file (image/jpeg, etc.)
    content_type: Optional[str] = None


class DBUploadModel(BaseModel):
    """
    Model representing a single file's metadata which will be uploaded to the db. 
    """
    id: str
    original_name: str
    filename: str
    file_path: str
    url: str
    upload_time: date
    size: int
    dimensions: dict
    status: str  # pending/processed/error
    caption: Optional[str] = None
    tags: List[str] = []
    faces: List = []
    face_cluster_ids: List = []

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60d21b4967d0d8992e610c85",
                "original_name": "vacation.jpg",
                "filename": "60d21b4967d0d8992e610c85.jpg",
                "file_path": "/uploads/images/60d21b4967d0d8992e610c85.jpg",
                "url": "http://example.com/uploads/images/60d21b4967d0d8992e610c85.jpg",
                "upload_time": "2023-08-01",
                "size": 1024000,
                "dimensions": {
                    "width": 1920,
                    "height": 1080
                },
                "status": "pending",
                "caption": "Beach vacation",
                "tags": [],
                "faces": [],
                "face_cluster_ids": []
            }
        }


class PaginatedUploadsResponse(BaseModel):
    """
    Model representing a paginated response for uploads.
    """
    data: List[dict]
    total: int
    page: int
    limit: int


class UploadSuccess(BaseModel):
    """
    Model representing a successful upload response.

    This is the overall response structure for the upload endpoint,
    containing a success message and a list of uploaded file information.
    """
    message: str             # A success message for the client
    data: List[UploadResponse]  # List of information about each uploaded file
