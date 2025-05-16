"""
Test script to verify MongoDB connection and operations.

This script initializes a MongoDB connection and performs basic operations
to verify that the connection is working correctly.

Usage:
    python test_mongodb.py
"""

import logging
import sys
from app.db.mongodb import init_mongodb, get_collection
from app.config import settings
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mongodb_test")


def test_mongodb():
    """Test MongoDB connection and operations"""
    logger.info("Testing MongoDB connection...")

    # Initialize MongoDB
    success = init_mongodb()
    if not success:
        logger.error("Failed to connect to MongoDB")
        return False

    logger.info("MongoDB connection successful")

    # Get the uploads collection
    uploads_collection = get_collection(settings.MONGODB_UPLOADS_COLLECTION)

    # Create a test document
    test_id = str(uuid.uuid4())
    test_doc = {
        "id": test_id,
        "original_name": "test.jpg",
        "filename": f"{test_id}.jpg",
        "file_path": f"/uploads/{test_id}.jpg",
        "url": f"http://example.com/uploads/{test_id}.jpg",
        "upload_time": datetime.now(),
        "size": 1024,
        "dimensions": {
            "width": 800,
            "height": 600
        },
        "status": "pending",
        "caption": None,
        "tags": ["test"],
        "faces": [],
        "face_cluster_ids": []
    }

    # Insert the test document
    logger.info(f"Inserting test document with ID: {test_id}")
    try:
        result = uploads_collection.insert_one(test_doc)
        logger.info(f"Insert successful, ID: {result.inserted_id}")
    except Exception as e:
        logger.error(f"Failed to insert test document: {str(e)}")
        return False

    # Retrieve the test document
    logger.info(f"Retrieving test document with ID: {test_id}")
    try:
        retrieved_doc = uploads_collection.find_one({"id": test_id})
        if retrieved_doc:
            logger.info(
                f"Document retrieved successfully: {retrieved_doc.get('original_name')}")
        else:
            logger.error(f"Document not found with ID: {test_id}")
            return False
    except Exception as e:
        logger.error(f"Failed to retrieve test document: {str(e)}")
        return False

    # Delete the test document
    logger.info(f"Deleting test document with ID: {test_id}")
    try:
        uploads_collection.delete_one({"id": test_id})
        logger.info("Document deleted successfully")
    except Exception as e:
        logger.error(f"Failed to delete test document: {str(e)}")
        return False

    logger.info("All MongoDB tests passed successfully")
    return True


if __name__ == "__main__":
    success = test_mongodb()
    sys.exit(0 if success else 1)
