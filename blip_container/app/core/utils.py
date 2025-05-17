import time
import os
from typing import List
import logging

from ..models.schemas import CaptionResponse
from ..model import generate_caption

logger = logging.getLogger(__name__)


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


def validate_image_path(image_path: str) -> bool:
    """
    Validate that an image path exists.

    Args:
        image_path: Path to check

    Returns:
        bool: True if path exists, False otherwise
    """
    return os.path.exists(image_path)
