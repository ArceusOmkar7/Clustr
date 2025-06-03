"""
Test script to verify caption service with tags functionality.

This script tests the updated caption service that now extracts both
captions and tags from the BLIP captioning microservice.

Usage:
    python test_caption_service.py
"""

import asyncio
import logging
import sys
import os
from app.ml.caption_service import get_image_caption_and_tags, get_image_caption, get_image_tags
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("caption_test")


async def test_caption_service():
    """Test caption service with tags functionality"""
    logger.info("Testing caption service with tags...")

    # Check if BLIP service URL is configured
    if not settings.BLIP_BASE_URL:
        logger.error("BLIP_BASE_URL not configured in settings")
        return False

    logger.info(f"Using BLIP service at: {settings.BLIP_BASE_URL}")

    # Find a test image
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    if not os.path.exists(uploads_dir):
        logger.error(f"Uploads directory not found: {uploads_dir}")
        return False

    # Get the first available image file
    test_image = None
    for filename in os.listdir(uploads_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            test_image = os.path.join(uploads_dir, filename)
            break

    if not test_image:
        logger.error("No test images found in uploads directory")
        return False

    logger.info(f"Testing with image: {os.path.basename(test_image)}")

    try:
        # Test the combined function
        logger.info("Testing get_image_caption_and_tags...")
        result = await get_image_caption_and_tags(test_image)

        if result:
            caption = result.get("caption")
            tags = result.get("tags", [])

            logger.info(f"✓ Caption: {caption}")
            logger.info(f"✓ Tags: {tags}")
            logger.info(f"✓ Number of tags: {len(tags)}")

            # Test individual functions
            logger.info("\nTesting individual functions...")

            caption_only = await get_image_caption(test_image)
            tags_only = await get_image_tags(test_image)

            logger.info(f"✓ Caption-only function: {caption_only}")
            logger.info(f"✓ Tags-only function: {tags_only}")

            # Verify consistency
            if caption == caption_only and tags == tags_only:
                logger.info("✓ Individual functions return consistent results")
            else:
                logger.warning(
                    "⚠ Individual functions returned different results")

            return True
        else:
            logger.error("✗ No result returned from caption service")
            return False

    except Exception as e:
        logger.error(f"✗ Error during testing: {str(e)}")
        return False


def main():
    """Main test function"""
    logger.info("Starting caption service test...")

    try:
        success = asyncio.run(test_caption_service())

        if success:
            logger.info("🎉 All caption service tests passed!")
            return True
        else:
            logger.error("❌ Caption service tests failed")
            return False

    except Exception as e:
        logger.error(f"❌ Test failed with exception: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
