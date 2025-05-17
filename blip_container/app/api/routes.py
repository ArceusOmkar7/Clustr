from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse
from typing import List
import time
import shutil
import os

from ..core.config import logger, UPLOAD_DIR
from ..models.schemas import CaptionRequest, CaptionResponse, BatchCaptionRequest, BatchCaptionResponse
from ..model import generate_caption
from ..core.utils import process_image_background, validate_image_path

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint to verify API status."""
    return {"status": "healthy", "service": "BLIP Image Captioning API"}


@router.get("/")
async def root():
    """Serve the web interface for testing."""
    return FileResponse("static/index.html")


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Handle file uploads and generate captions.

    Args:
        files: List of uploaded image files

    Returns:
        BatchCaptionResponse containing captions and processing times
    """
    start_time = time.time()
    results = []

    for file in files:
        try:
            # Save uploaded file to disk
            file_path = UPLOAD_DIR / file.filename
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Generate caption for the image
            caption = generate_caption(str(file_path))

            # Calculate processing time
            processing_time = time.time() - start_time

            results.append(CaptionResponse(
                image_path=str(file_path),
                caption=caption,
                processing_time=processing_time
            ))

        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            continue

    return BatchCaptionResponse(
        results=results,
        total_processing_time=time.time() - start_time
    )


@router.post("/caption", response_model=CaptionResponse)
async def caption_image(request: CaptionRequest):
    """
    Generate caption for a single image.

    Args:
        request: CaptionRequest containing image path

    Returns:
        CaptionResponse with generated caption

    Raises:
        HTTPException: If image not found or processing fails
    """
    start_time = time.time()

    try:
        # Validate image path exists
        if not validate_image_path(request.image_path):
            raise HTTPException(
                status_code=404, detail=f"Image not found: {request.image_path}")

        # Generate caption
        caption = generate_caption(request.image_path)

        # Calculate processing time
        processing_time = time.time() - start_time

        return CaptionResponse(
            image_path=request.image_path,
            caption=caption,
            processing_time=processing_time
        )

    except Exception as e:
        logger.error(f"Error processing image {request.image_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-caption", response_model=BatchCaptionResponse)
async def batch_caption_images(request: BatchCaptionRequest):
    """
    Generate captions for multiple images.

    Args:
        request: BatchCaptionRequest containing list of image paths

    Returns:
        BatchCaptionResponse with results for all successfully processed images
    """
    start_time = time.time()
    results = []

    for image_path in request.image_paths:
        try:
            # Validate image path exists
            if not validate_image_path(image_path):
                logger.warning(f"Image not found: {image_path}")
                continue

            # Generate caption
            caption = generate_caption(image_path)

            # Calculate processing time for this image
            processing_time = time.time() - start_time

            results.append(CaptionResponse(
                image_path=image_path,
                caption=caption,
                processing_time=processing_time
            ))

        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            # Continue with other images even if one fails

    # Calculate total processing time
    total_processing_time = time.time() - start_time

    return BatchCaptionResponse(
        results=results,
        total_processing_time=total_processing_time
    )


@router.post("/async-batch-caption", response_model=BatchCaptionResponse)
async def async_batch_caption_images(request: BatchCaptionRequest, background_tasks: BackgroundTasks):
    """
    Process multiple images asynchronously using background tasks.

    Args:
        request: BatchCaptionRequest containing list of image paths
        background_tasks: FastAPI background tasks handler

    Returns:
        BatchCaptionResponse with results for all successfully processed images
    """
    start_time = time.time()
    results = []

    # Add each image to background tasks
    for image_path in request.image_paths:
        if validate_image_path(image_path):
            background_tasks.add_task(
                process_image_background, image_path, results, start_time)
        else:
            logger.warning(f"Image not found: {image_path}")

    # Calculate total processing time
    total_processing_time = time.time() - start_time

    return BatchCaptionResponse(
        results=results,
        total_processing_time=total_processing_time
    )
