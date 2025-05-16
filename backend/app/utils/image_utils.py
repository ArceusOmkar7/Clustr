from PIL import Image
from typing import Dict, Tuple
import logging
import os
import traceback

# Configure logger
logger = logging.getLogger(__name__)


def get_image_dimensions(file_path: str) -> Dict[str, int]:
    """
    Get the dimensions of an image file.

    Args:
        file_path: Path to the image file

    Returns:
        Dict containing width and height
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {"width": 0, "height": 0}

        # Standard handling for common formats
        with Image.open(file_path) as img:
            width, height = img.size
            logger.info(f"Got dimensions for {file_path}: {width}x{height}")
            return {
                "width": width,
                "height": height
            }
    except Exception as e:
        logger.error(f"Error getting dimensions for {file_path}: {str(e)}")
        logger.debug(traceback.format_exc())
        # Return default dimensions if the file cannot be opened
        return {
            "width": 0,
            "height": 0
        }
