import httpx
import logging
import os
from typing import Optional
from app.config import settings
from app.services.mongodb_service import mongodb_service  # Import mongodb_service

logger = logging.getLogger(__name__)


async def generate_caption_and_update_db(image_path: str, image_id: str):
    """
    Asynchronously generates a caption and tags for the image and updates the database.
    This function is intended to be run as a background task.

    Args:
        image_path: The absolute path to the image file on the host machine.
        image_id: The unique ID of the image in the database.
    """
    logger.info(
        f"Starting background caption generation for image_id: {image_id} at path: {image_path}")
    caption = None
    try:
        if not os.path.exists(image_path):
            logger.error(
                f"Background task: Host image path does not exist: {image_path} for image_id: {image_id}")
            mongodb_service.update_upload_metadata(
                image_id, {"status": "caption_failed_file_not_found"})
            return

        caption_endpoint = "/caption"
        full_blip_url = f"{settings.BLIP_BASE_URL}{caption_endpoint}"

        with open(image_path, "rb") as image_file:
            files = {"image": (os.path.basename(image_path),
                               image_file, "image/jpeg")}

            async with httpx.AsyncClient() as client:
                logger.info(
                    f"Background task: Requesting caption for image_id: {image_id} from {full_blip_url}")
                response = await client.post(full_blip_url, files=files, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                caption = data.get("caption")
                # Extract tags, default to empty list
                tags = data.get("tags", [])
                logger.info(
                    f"Background task: Received caption for image_id: {image_id}: {caption}")
                logger.info(
                    f"Background task: Received tags for image_id: {image_id}: {tags}")

        if caption:
            update_data = {"caption": caption,
                           "tags": tags, "status": "processed"}
            success = mongodb_service.update_upload_metadata(
                image_id, update_data)
            if success:
                logger.info(
                    f"Successfully updated DB for image_id: {image_id} with caption and tags.")
            else:
                logger.error(
                    f"Failed to update DB for image_id: {image_id} with caption and tags.")
        else:
            logger.warning(
                f"Background task: No caption received for image_id: {image_id}. Status remains pending_caption or will be caption_failed.")
            mongodb_service.update_upload_metadata(
                image_id, {"status": "caption_failed_no_caption"})

    except FileNotFoundError:
        logger.error(
            f"Background task: File not found at path: {image_path} for image_id: {image_id}")
        mongodb_service.update_upload_metadata(
            image_id, {"status": "caption_failed_file_not_found"})
    except httpx.RequestError as e:
        logger.error(
            f"Background task: HTTP request to BLIP service failed for image_id: {image_id}: {e}")
        mongodb_service.update_upload_metadata(
            image_id, {"status": "caption_failed_http_error"})
    except Exception as e:
        logger.error(
            f"Background task: An unexpected error occurred for image_id: {image_id}: {e}")
        mongodb_service.update_upload_metadata(
            image_id, {"status": "caption_failed_unexpected"})

# Original get_image_caption can be kept if direct synchronous calls are ever needed elsewhere,
# or removed if all captioning will go through the background task.
# For now, let's assume it might be useful for testing or other specific scenarios.


async def get_image_caption_and_tags(image_path: str) -> Optional[dict]:
    """
    Calls the BLIP image captioning microservice to get both caption and tags for the given image.
    This is a direct, synchronous call.

    Args:
        image_path: The absolute path to the image file on the host machine.

    Returns:
        A dictionary with 'caption' and 'tags' keys if successful, None otherwise.
    """
    if not os.path.exists(image_path):
        logger.error(f"Host image path does not exist: {image_path}")
        return None

    caption_endpoint = "/caption"
    full_blip_url = f"{settings.BLIP_BASE_URL}{caption_endpoint}"

    try:
        with open(image_path, "rb") as image_file:
            files = {"image": (os.path.basename(image_path),
                               image_file, "image/jpeg")}

            async with httpx.AsyncClient() as client:
                logger.info(
                    f"Requesting caption and tags for {image_path} (sending file) from {full_blip_url}")
                response = await client.post(full_blip_url, files=files, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                caption = data.get("caption")
                tags = data.get("tags", [])
                logger.info(f"Received caption for {image_path}: {caption}")
                logger.info(f"Received tags for {image_path}: {tags}")
                return {"caption": caption, "tags": tags}
    except FileNotFoundError:
        logger.error(f"File not found at path: {image_path}")
    except httpx.RequestError as e:
        logger.error(
            f"HTTP request to BLIP service failed for {image_path}: {e}")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while getting caption and tags for {image_path}: {e}")
    return None


async def get_image_caption(image_path: str) -> Optional[str]:
    """
    Calls the BLIP image captioning microservice to get a caption for the given image.
    This is a direct, synchronous call.

    Args:
        image_path: The absolute path to the image file on the host machine.

    Returns:
        The generated caption string if successful, None otherwise.
    """
    result = await get_image_caption_and_tags(image_path)
    return result.get("caption") if result else None


async def get_image_tags(image_path: str) -> list[str]:
    """
    Calls the BLIP image captioning microservice to get tags for the given image.
    This function now uses the BLIP service instead of being a placeholder.

    Args:
        image_path: The absolute path to the image file on the host machine.

    Returns:
        A list of tags for the image if successful, empty list otherwise.
    """
    result = await get_image_caption_and_tags(image_path)
    return result.get("tags", []) if result else []


async def detect_faces(image_path: str) -> list[dict]:
    """
    (Placeholder) In the future, this function will call a service for face detection.
    For now, it returns an empty list.
    """
    logger.info(f"Face detection not yet implemented for {image_path}.")
    return []
