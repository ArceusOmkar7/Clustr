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
from app.ml.caption_service import get_image_caption  # Added import

# Configure logger for this module
logger = logging.getLogger(__name__)


async def upload_files_service(files: List[UploadFile]) -> UploadSuccess:
    """
    Process and store uploaded files.

    This service function handles the complete business logic for file uploads:
    1. Validates that files were provided in the request
    2. Checks each file against allowed extensions (security measure)
    3. Saves valid files to the upload directory with unique filenames
    4. Extracts image metadata like dimensions using Pillow
    5. Saves comprehensive metadata to MongoDB for future use
    6. Generates preview URLs for client access
    7. Returns a standardized response with information about uploaded files

    The function is designed to be robust, with error handling at each step,
    ensuring that even if MongoDB is unavailable, the upload still works.

    Parameters:
    - files: List of FastAPI UploadFile objects from the request

    Returns:
    - UploadSuccess: Object containing success message and file metadata

    Raises:
    - HTTPException: If no files are found in the request (406)
    - No exceptions for individual file failures - these are logged but don't affect other files
    """
    # Validate that files were provided
    if not files:
        # Use the helper function to raise a standardized HTTP error
        send_error("No files found in request", 406)

    # List to collect information about successfully uploaded files
    uploaded_files = []

    # Process each file in the request
    for file in files:
        # Skip files with disallowed extensions (security measure)
        if not allowed_file(file.filename):
            logger.warning(f"File type not allowed: {file.filename}")
            continue

        # Generate a unique filename to prevent overwriting and path traversal attacks
        unique_id = str(uuid.uuid4())
        original_filename = file.filename
        extension = original_filename.rsplit(
            '.', 1)[1].lower() if '.' in original_filename else ''
        filename = f"{unique_id}.{extension}" if extension else unique_id

        # Create full file path in the configured uploads directory
        file_path = os.path.join(settings.UPLOAD_FOLDER, filename)

        # Ensure the UPLOAD_FOLDER exists
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

        # Save the file to the uploads directory
        try:
            with open(file_path, "wb") as fb:
                shutil.copyfileobj(file.file, fb)
            logger.info(f"File saved to {file_path}")
        except Exception as e:
            logger.error(
                f"Failed to save file {original_filename} to {file_path}: {e}")
            # Optionally, you might want to skip this file and continue with others
            # or raise an HTTPException here if saving is critical.
            continue  # Skip to the next file if saving failed

        # Create a fully qualified preview URL for the client to access the file
        # Example: "http://127.0.0.1:5000/uploads/image.jpg"
        preview_url = f"{settings.BASE_URL}{settings.UPLOAD_URL_PATH}/{filename}"

        # Get image dimensions with proper error handling
        try:
            dimensions = get_image_dimensions(file_path)
            logger.info(f"Image dimensions for {filename}: {dimensions}")
        except Exception as e:
            logger.error(
                f"Failed to get image dimensions for {filename}: {str(e)}")
            dimensions = {"width": 0, "height": 0}

        # Get image caption from BLIP service
        caption = None
        try:
            # Ensure file_path is absolute for the captioning service
            absolute_file_path = os.path.abspath(file_path)
            caption = await get_image_caption(absolute_file_path)
            if caption:
                logger.info(f"Caption for {filename}: {caption}")
            else:
                logger.warning(f"No caption received for {filename}")
        except Exception as e:
            logger.error(f"Failed to get caption for {filename}: {e}")

        # Create comprehensive metadata for MongoDB storage
        upload_metadata = {
            "id": unique_id,
            "original_name": original_filename,
            "filename": filename,
            # Storing relative path might be better if service runs in different env
            "file_path": file_path,
            "url": preview_url,
            "upload_time": datetime.now(),  # Use timezone-aware datetime if possible
            "size": file.size,
            "dimensions": dimensions,
            # Update status based on captioning
            "status": "processed" if caption else "pending_caption",
            "caption": caption,  # Store the caption
            "tags": [],  # To be populated later
            "faces": [],  # For future face detection
            "face_cluster_ids": []  # For future face clustering
        }

        # Save metadata to MongoDB with error handling
        try:
            mongodb_service.save_upload_metadata(upload_metadata)
            logger.info(f"Metadata saved to MongoDB for file: {filename}")
        except Exception as e:
            # Log the error but continue processing
            # This allows the application to work even if MongoDB isn't available
            logger.error(f"Failed to save metadata to MongoDB: {str(e)}")

        # Add metadata about this file to our list of successfully uploaded files
        # This creates the response object that will be returned to the client
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
