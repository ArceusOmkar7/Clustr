from app.config import settings
from app.db.mongodb import get_collection, get_db
import uuid
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logger
logger = logging.getLogger(__name__)


class MongoDBService:
    """
    Service for interacting with MongoDB.
    Provides methods to perform operations on the database.

    This service abstracts MongoDB operations for other parts of the application,
    providing simple methods for storing and retrieving file metadata.
    It includes error handling and connection management.
    """

    def __init__(self):
        """
        Initialize the MongoDB service.
        Tries to establish a connection to the configured MongoDB collection.
        Sets an internal flag to track connection status.
        """
        # Get the uploads collection
        try:
            self.uploads_collection = get_collection(
                settings.MONGODB_UPLOADS_COLLECTION)
            self.is_connected = True
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB service: {str(e)}")
            self.is_connected = False

    def save_upload_metadata(self, metadata: Dict[str, Any]) -> str:
        """
        Save upload metadata to MongoDB

        Args:
            metadata: Dictionary containing metadata for the uploaded file
                     Should include fields like id, filename, dimensions, etc.

        Returns:
            str: ID of the inserted document (either the original ID from metadata
                 or a newly generated one if insertion failed)

        This method handles MongoDB connection errors gracefully, allowing
        the application to continue running even if metadata storage fails.
        """
        if not self.is_connected:
            logger.warning("MongoDB is not connected, skipping metadata save")
            return metadata.get('id', str(uuid.uuid4()))

        try:
            # Generate an ID if none is provided
            if 'id' not in metadata:
                metadata['id'] = str(uuid.uuid4())

            # Insert metadata into MongoDB
            result = self.uploads_collection.insert_one(metadata)

            # Return the ID of the inserted document
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving metadata to MongoDB: {str(e)}")
            return metadata.get('id', str(uuid.uuid4()))

    def get_upload_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Retrieve upload metadata from MongoDB

        Args:
            file_id: ID of the document to retrieve

        Returns:
            Dict: Metadata for the uploaded file, or None if not found
                  or if an error occurred
        """
        if not self.is_connected:
            logger.warning(
                "MongoDB is not connected, cannot retrieve metadata")
            return None

        try:
            # Find the document by ID
            return self.uploads_collection.find_one({"id": file_id})
        except Exception as e:
            logger.error(f"Error retrieving metadata from MongoDB: {str(e)}")
            return None

    def get_all_uploads(self) -> List[Dict[str, Any]]:
        """
        Retrieve all uploads

        Returns:
            List: All upload metadata, or empty list if none found
                  or if an error occurred

        The '_id' field is excluded from the results to avoid serialization
        issues with ObjectId.
        """
        if not self.is_connected:
            logger.warning("MongoDB is not connected, cannot retrieve uploads")
            return []

        try:
            # Find all documents in the collection, excluding MongoDB's _id field
            return list(self.uploads_collection.find({}, {'_id': 0}))
        except Exception as e:
            logger.error(
                f"Error retrieving all uploads from MongoDB: {str(e)}")
            return []

    def get_paginated_uploads(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        Retrieve uploads with pagination

        Args:
            page: Page number (1-indexed)
            limit: Number of items per page

        Returns:
            Dict: Contains data (list of uploads), total count, page number, and limit
        """
        if not self.is_connected:
            logger.warning(
                "MongoDB is not connected, cannot retrieve paginated uploads")
            return {"data": [], "total": 0, "page": page, "limit": limit}

        try:
            # Calculate skip value (number of documents to skip)
            skip = (page - 1) * limit

            # Get total count
            total = self.uploads_collection.count_documents({})

            # Get paginated results
            uploads = list(self.uploads_collection
                           .find({}, {'_id': 0})
                           # Sort by upload time descending (newest first)
                           .sort("upload_time", -1)
                           .skip(skip)
                           .limit(limit))

            return {
                "data": uploads,
                "total": total,
                "page": page,
                "limit": limit
            }
        except Exception as e:
            logger.error(
                f"Error retrieving paginated uploads from MongoDB: {str(e)}")
            return {"data": [], "total": 0, "page": page, "limit": limit}


# Create a global instance of the MongoDB service
mongodb_service = MongoDBService()
