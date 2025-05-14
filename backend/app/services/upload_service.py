from fastapi import UploadFile
from typing import List
import os
import shutil
from app.config import settings
from app.utils.helpers import allowed_file, send_error
from app.models.upload_models import UploadSuccess, UploadResponse


async def upload_files_service(files: List[UploadFile]) -> UploadSuccess:
    """
    Process and store uploaded files.

    This service function handles the business logic for file uploads:
    1. Validates that files were provided in the request
    2. Checks each file against allowed extensions
    3. Saves valid files to the upload directory
    4. Generates metadata including preview URLs
    5. Returns a standardized response with information about uploaded files

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

        # Get the original filename - in a production app, you'd want to sanitize this
        # and generate a unique name to prevent overwriting and path traversal attacks
        filename = file.filename
        file_path = os.path.join(settings.UPLOAD_FOLDER, filename)

        # Save the file to the uploads directory
        # The with statement ensures the file is properly closed after writing
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create a fully qualified preview URL for the client to access the file
        # Example: "http://127.0.0.1:5000/uploads/image.jpg"
        preview_url = f"{settings.BASE_URL}{settings.UPLOAD_URL_PATH}/{filename}"

        # Add metadata about this file to our list of successfully uploaded files
        uploaded_files.append(UploadResponse(
            stored_filename=filename,
            original_filename=filename,
            file_size=file.size,
            preview_url=preview_url,
            content_type=file.content_type
        ))

    # Return a success response with information about all uploaded files
    return UploadSuccess(
        message=f"Successfully uploaded {len(uploaded_files)} files",
        data=uploaded_files
    )
