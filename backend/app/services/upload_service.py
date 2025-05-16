from fastapi import UploadFile
from typing import List
import os
import shutil
import uuid
from datetime import datetime
from app.config import settings
from app.utils.helpers import allowed_file, send_error
from app.utils.image_utils import get_image_dimensions
from app.models.upload_models import UploadSuccess, UploadResponse, DBUploadModel
from app.services.mongodb_service import mongodb_service
import logging

logger = logging.getLogger(__name__)


async def upload_files_service(files: List[UploadFile]) -> UploadSuccess:
    """
    Process and store uploaded files.

    This service function handles the business logic for file uploads:
    1. Validates that files were provided in the request
    2. Checks each file against allowed extensions
    3. Saves valid files to the upload directory
    4. Generates metadata including preview URLs
    5. Saves metadata to MongoDB
    6. Returns a standardized response with information about uploaded files

    Parameters:
    - files: List of FastAPI UploadFile objects from the request

    Returns:
    - UploadSuccess: Object containing success message and file metadata

    Raises:
    - HTTPException: If no files are found in the request
    """
    # Validate that files were provided
    if not files:
        # Use the helper function to raise a standardized HTTP error
        send_error("No files found in request", 406)

    # List to collect information about successfully uploaded files
    uploaded_files = []

    # Process each file in the request
    for file in files:
        # Skip files with disallowed extensions
        if not allowed_file(file.filename):
            continue

        # Generate a unique filename to prevent overwriting
        unique_id = str(uuid.uuid4())
        original_filename = file.filename
        extension = original_filename.rsplit(
            '.', 1)[1].lower() if '.' in original_filename else ''
        filename = f"{unique_id}.{extension}" if extension else unique_id

        file_path = os.path.join(settings.UPLOAD_FOLDER, filename)

        # Save the file to the uploads directory
        with open(file_path, "wb") as fb:
            shutil.copyfileobj(file.file, fb)

        # Create a fully qualified preview URL for the client to access the file
        # Example: "http://127.0.0.1:5000/uploads/image.jpg"
        preview_url = f"{settings.BASE_URL}{settings.UPLOAD_URL_PATH}/{filename}"

        # Get image dimensions
        dimensions = get_image_dimensions(file_path)

        # Create metadata for MongoDB
        upload_metadata = {
            "id": unique_id,
            "original_name": original_filename,
            "filename": filename,
            "file_path": file_path,
            "url": preview_url,
            "upload_time": datetime.now(),
            "size": file.size,
            "dimensions": dimensions,
            "status": "pending",
            "caption": None,
            "tags": [],
            "faces": [],
            "face_cluster_ids": []
        }

        # Save metadata to MongoDB
        try:
            mongodb_service.save_upload_metadata(upload_metadata)
        except Exception as e:
            # Log the error but continue processing
            # This allows the application to work even if MongoDB isn't available
            logger.error(f"Failed to save metadata to MongoDB: {str(e)}")

        # Add metadata about this file to our list of successfully uploaded files
        uploaded_files.append(UploadResponse(
            stored_filename=filename,
            original_filename=original_filename,
            file_size=file.size,
            preview_url=preview_url,
            content_type=file.content_type
        ))

    # Return a success response with information about all uploaded files
    return UploadSuccess(
        message=f"Successfully uploaded {len(uploaded_files)} files",
        data=uploaded_files
    )
