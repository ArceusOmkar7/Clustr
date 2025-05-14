from fastapi import UploadFile
from typing import List
import os
import shutil
from app.config import settings
from app.utils.helpers import allowed_file, send_error
from app.models.upload_models import UploadSuccess, UploadResponse


async def upload_files_service(files: List[UploadFile]) -> UploadSuccess:
    if not files:
        send_error("No files found in request", 406)

    uploaded_files = []

    for file in files:
        if not allowed_file(file.filename):
            continue

        # Secure the filename
        filename = file.filename
        file_path = os.path.join(settings.UPLOAD_FOLDER, filename)

        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create a preview URL (can be customized as needed)
        preview_url = f"/uploads/{filename}"

        uploaded_files.append(UploadResponse(
            stored_filename=filename,
            original_filename=filename,
            file_size=file.size,
            preview_url=preview_url,
            content_type=file.content_type
        ))

    return UploadSuccess(
        message=f"Successfully uploaded {len(uploaded_files)} files",
        data=uploaded_files
    )
