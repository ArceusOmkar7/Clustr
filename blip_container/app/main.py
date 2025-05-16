"""
BLIP Image Captioning API
-------------------------
This FastAPI application provides endpoints for generating captions for images using the BLIP model.
It includes both a REST API and a web interface for testing.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import logging
import os
from typing import List, Optional
import time
import shutil
from pathlib import Path

from .model import generate_caption

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app with metadata
app = FastAPI(
    title="BLIP Image Captioning API",
    description="API for generating captions for images using the BLIP model",
    version="1.0.0"
)

# Configure CORS to allow requests from any origin (customize for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory for storing temporary image files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files directory for serving the web interface
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for request/response validation


class CaptionRequest(BaseModel):
    """Request model for single image captioning."""
    image_path: str


class CaptionResponse(BaseModel):
    """Response model containing caption and metadata."""
    image_path: str
    caption: str
    processing_time: float


class BatchCaptionRequest(BaseModel):
    """Request model for batch image captioning."""
    image_paths: List[str]


class BatchCaptionResponse(BaseModel):
    """Response model for batch captioning results."""
    results: List[CaptionResponse]
    total_processing_time: float

# API Endpoints


@app.get("/health")
async def health_check():
    """Health check endpoint to verify API status."""
    return {"status": "healthy", "service": "BLIP Image Captioning API"}


@app.get("/")
async def root():
    """Serve the web interface for testing."""
    return FileResponse("static/index.html")


@app.post("/upload")
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


@app.post("/caption", response_model=CaptionResponse)
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
        if not os.path.exists(request.image_path):
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


@app.post("/batch-caption", response_model=BatchCaptionResponse)
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
            if not os.path.exists(image_path):
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


async def process_image_background(image_path: str, results: List[CaptionResponse], start_time: float):
    """
    Background task for processing a single image.

    Args:
        image_path: Path to the image file
        results: List to append results to
        start_time: Start time for processing time calculation
    """
    try:
        caption = generate_caption(image_path)
        processing_time = time.time() - start_time

        results.append(CaptionResponse(
            image_path=image_path,
            caption=caption,
            processing_time=processing_time
        ))
    except Exception as e:
        logger.error(
            f"Error in background processing for {image_path}: {str(e)}")


@app.post("/async-batch-caption", response_model=BatchCaptionResponse)
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
        if os.path.exists(image_path):
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
