from pydantic import BaseModel
from typing import List, Optional


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


class UploadSuccess(BaseModel):
    """
    Model representing a successful upload response.

    This is the overall response structure for the upload endpoint,
    containing a success message and a list of uploaded file information.
    """
    message: str             # A success message for the client
    data: List[UploadResponse]  # List of information about each uploaded file
