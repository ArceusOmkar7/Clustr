from PIL import Image
from typing import Dict, Tuple


def get_image_dimensions(file_path: str) -> Dict[str, int]:
    """
    Get the dimensions of an image file.

    Args:
        file_path: Path to the image file

    Returns:
        Dict containing width and height
    """
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            return {
                "width": width,
                "height": height
            }
    except Exception:
        # Return default dimensions if the file cannot be opened
        return {
            "width": 0,
            "height": 0
        }
