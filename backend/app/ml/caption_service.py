import httpx
import logging
import os
from typing import Optional
from app.config import settings  # Import settings

logger = logging.getLogger(__name__)


async def get_image_caption(image_path: str) -> Optional[str]:
    """
    Calls the BLIP image captioning microservice to get a caption for the given image.

    Args:
        image_path: The absolute path to the image file on the host machine.

    Returns:
        The generated caption string if successful, None otherwise.
    """
    if not os.path.exists(image_path):
        logger.error(f"Host image path does not exist: {image_path}")
        return None

    caption_endpoint = "/caption"
    full_blip_url = f"{settings.BLIP_BASE_URL}{caption_endpoint}"

    try:
        with open(image_path, "rb") as image_file:
            # Assuming JPEG, adjust if needed or determine dynamically
            files = {"image": (os.path.basename(image_path),
                               image_file, "image/jpeg")}

            async with httpx.AsyncClient() as client:
                logger.info(
                    f"Requesting caption for {image_path} (sending file) from {full_blip_url}")
                # Increased timeout for file upload
                response = await client.post(full_blip_url, files=files, timeout=60.0)
                response.raise_for_status()

                data = response.json()
                caption = data.get("caption")
                logger.info(f"Received caption for {image_path}: {caption}")
                return caption
    except FileNotFoundError:
        logger.error(f"File not found at path: {image_path}")
    except httpx.RequestError as e:
        logger.error(
            f"HTTP request to BLIP service failed for {image_path}: {e}")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while getting caption for {image_path}: {e}")

    return None


async def get_image_tags(image_path: str) -> list[str]:
    """
    (Placeholder) In the future, this function will call a service to get tags for an image.
    For now, it returns an empty list.
    """
    logger.info(f"Tag generation not yet implemented for {image_path}.")
    return []


async def detect_faces(image_path: str) -> list[dict]:
    """
    (Placeholder) In the future, this function will call a service for face detection.
    For now, it returns an empty list.
    """
    logger.info(f"Face detection not yet implemented for {image_path}.")
    return []
