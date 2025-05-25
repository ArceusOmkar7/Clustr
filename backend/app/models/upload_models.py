from pydantic import BaseModel, Field
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
    status: str  # e.g., pending_upload, pending_caption, processed, error
    caption: Optional[str] = None
    # Ensure default is a new list
    tags: List[str] = Field(default_factory=list)
    # Store face detection results, e.g., bounding boxes
    faces: List[dict] = Field(default_factory=list)
    face_cluster_ids: List[str] = Field(
        default_factory=list)  # IDs linking to face clusters

    class Config:
        validate_assignment = True  # Ensures that model fields are validated on assignment
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
                "status": "processed",
                "caption": "A beautiful landscape with mountains and a lake.",
                "tags": ["landscape", "mountains", "lake", "nature"],
                "faces": [
                    {"box": [100, 150, 50, 50], "confidence": 0.98,
                        "embedding_id": "face_emb_1"}
                ],
                "face_cluster_ids": ["cluster_A"]
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
