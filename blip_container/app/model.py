"""
BLIP Image Captioning Model
--------------------------
This module provides functionality for generating captions for images using the BLIP model.
It handles model loading, image processing, and caption generation.
"""

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set device (GPU if available, otherwise CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {device}")

# Load BLIP model and processor
try:
    # Initialize the BLIP processor for image preprocessing
    processor = BlipProcessor.from_pretrained(
        "Salesforce/blip-image-captioning-base")

    # Initialize the BLIP model for caption generation
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    ).to(device)

    logger.info("BLIP model and processor loaded successfully")
except Exception as e:
    logger.error(f"Error loading BLIP model: {str(e)}")
    raise


def generate_caption(image_path: str) -> str:
    """
    Generate a caption for an image using the BLIP model.

    This function:
    1. Loads and preprocesses the image
    2. Generates a caption using the BLIP model
    3. Returns the generated caption

    Args:
        image_path (str): Path to the image file

    Returns:
        str: Generated caption describing the image

    Raises:
        FileNotFoundError: If the image file doesn't exist
        ValueError: If the image file is invalid or can't be processed
        Exception: For other unexpected errors
    """
    try:
        # Load and convert image to RGB format
        image = Image.open(image_path).convert("RGB")

        # Preprocess image for the BLIP model
        inputs = processor(images=image, return_tensors="pt").to(device)

        # Generate caption
        output = model.generate(**inputs)

        # Decode the generated tokens into text
        caption = processor.decode(output[0], skip_special_tokens=True)

        logger.info(f"Generated caption for {image_path}: {caption}")
        return caption

    except FileNotFoundError:
        logger.error(f"Image file not found: {image_path}")
        raise
    except Exception as e:
        logger.error(f"Error generating caption for {image_path}: {str(e)}")
        raise
