from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Dict, Any, Optional
from app.ml.batch_caption_service import (
    batch_caption_service,
    queue_batch_caption_background_task,
    BatchCaptionRequest
)
from app.services.mongodb_service import mongodb_service
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/batch-process-uncaptioned")
async def batch_process_uncaptioned_images(
    background_tasks: BackgroundTasks,
    limit: int = Query(
        50, ge=1, le=200, description="Maximum number of images to process"),
    use_async: bool = Query(True, description="Use async batch processing")
):
    """
    Batch process uncaptioned images from the database.

    This endpoint finds images that don't have captions yet and processes them
    in batches using the BLIP service's batch endpoints.

    Parameters:
    - limit: Maximum number of images to process (default 50, max 200)
    - use_async: Whether to use async batch processing (recommended for large batches)

    Returns:
    - Information about the batch processing task
    """
    try:
        # Find uncaptioned images
        uncaptioned_images = mongodb_service.find_uncaptioned_images(limit)

        if not uncaptioned_images:
            return {
                "message": "No uncaptioned images found",
                "count": 0
            }

        logger.info(
            f"Found {len(uncaptioned_images)} uncaptioned images to process")

        # Prepare batch requests
        batch_requests = []
        for img in uncaptioned_images:
            image_path = img.get("file_path")
            if image_path and os.path.exists(image_path):
                batch_requests.append((
                    img["id"],
                    image_path,
                    img.get("original_name", f"image_{img['id']}")
                ))
            else:
                logger.warning(
                    f"Image file not found: {image_path} for ID {img.get('id')}")
                # Mark as failed
                mongodb_service.update_upload_metadata(
                    img["id"],
                    {"status": "caption_failed_file_not_found"}
                )

        if not batch_requests:
            return {
                "message": "No valid image files found for processing",
                "count": 0
            }

        # Add batch processing task
        background_tasks.add_task(
            queue_batch_caption_background_task,
            batch_requests
        )

        # Update status of images to indicate processing has started
        for image_id, _, _ in batch_requests:
            mongodb_service.update_upload_metadata(
                image_id,
                {"status": "processing_caption"}
            )

        return {
            "message": f"Batch processing started for {len(batch_requests)} images",
            "count": len(batch_requests),
            "processing_type": "async" if use_async else "sync"
        }

    except Exception as e:
        logger.error(f"Error in batch processing endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/async-task-status/{task_id}")
async def get_async_task_status(task_id: str):
    """
    Check the status of an async batch captioning task.

    Parameters:
    - task_id: The task ID returned by the BLIP service

    Returns:
    - Task status information from the BLIP service
    """
    try:
        status = await batch_caption_service.check_async_task_status(task_id)

        if status is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found or service unavailable"
            )

        return status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking task status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/caption-stats")
async def get_caption_statistics():
    """
    Get statistics about image captioning status.

    Returns:
    - Statistics about captioned vs uncaptioned images
    """
    try:
        stats = mongodb_service.get_caption_statistics()
        return stats

    except Exception as e:
        logger.error(f"Error getting caption statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recaption-images")
async def recaption_images(
    background_tasks: BackgroundTasks,
    image_ids: List[str],
    force: bool = Query(
        False, description="Force recaptioning even if caption exists")
):
    """
    Recaption specific images by their IDs.

    Parameters:
    - image_ids: List of image IDs to recaption
    - force: Whether to recaption images that already have captions

    Returns:
    - Information about the recaptioning task
    """
    try:
        if not image_ids:
            raise HTTPException(
                status_code=400, detail="No image IDs provided")

        if len(image_ids) > 100:
            raise HTTPException(
                status_code=400,
                detail="Maximum 100 images can be recaptioned at once"
            )

        # Get image metadata
        batch_requests = []
        not_found = []
        already_captioned = []

        for image_id in image_ids:
            img_metadata = mongodb_service.get_upload_metadata(image_id)

            if not img_metadata:
                not_found.append(image_id)
                continue

            # Check if already captioned and force flag
            if not force and img_metadata.get("caption"):
                already_captioned.append(image_id)
                continue

            image_path = img_metadata.get("file_path")
            if image_path and os.path.exists(image_path):
                batch_requests.append((
                    image_id,
                    image_path,
                    img_metadata.get("original_name", f"image_{image_id}")
                ))
            else:
                logger.warning(
                    f"Image file not found: {image_path} for ID {image_id}")
                mongodb_service.update_upload_metadata(
                    image_id,
                    {"status": "caption_failed_file_not_found"}
                )

        if batch_requests:
            # Add batch processing task
            background_tasks.add_task(
                queue_batch_caption_background_task,
                batch_requests
            )

            # Update status
            for image_id, _, _ in batch_requests:
                mongodb_service.update_upload_metadata(
                    image_id,
                    {"status": "processing_caption"}
                )

        return {
            "message": f"Recaptioning started for {len(batch_requests)} images",
            "processing_count": len(batch_requests),
            "not_found": not_found,
            "already_captioned": already_captioned if not force else [],
            "total_requested": len(image_ids)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in recaption endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-health")
async def check_blip_service_health():
    """
    Check if the BLIP captioning service is available and healthy.

    Returns:
    - Health status of the BLIP service
    """
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            health_url = f"{settings.BLIP_BASE_URL}/health"
            response = await client.get(health_url)
            response.raise_for_status()

            service_status = response.json()

            return {
                "blip_service_available": True,
                "blip_service_url": settings.BLIP_BASE_URL,
                "blip_service_status": service_status,
                "message": "BLIP service is healthy and available"
            }

    except httpx.RequestError as e:
        logger.error(f"BLIP service health check failed: {e}")
        return {
            "blip_service_available": False,
            "blip_service_url": settings.BLIP_BASE_URL,
            "error": str(e),
            "message": "BLIP service is not available"
        }
    except Exception as e:
        logger.error(f"Unexpected error during BLIP service health check: {e}")
        return {
            "blip_service_available": False,
            "blip_service_url": settings.BLIP_BASE_URL,
            "error": str(e),
            "message": "Error checking BLIP service health"
        }
