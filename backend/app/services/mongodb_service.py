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
    """

    def __init__(self):
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

        Returns:
            str: ID of the inserted document
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
            Dict: Metadata for the uploaded file
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
            List: All upload metadata
        """
        if not self.is_connected:
            logger.warning("MongoDB is not connected, cannot retrieve uploads")
            return []

        try:
            return list(self.uploads_collection.find({}, {'_id': 0}))
        except Exception as e:
            logger.error(
                f"Error retrieving all uploads from MongoDB: {str(e)}")
            return []


# Create a global instance of the MongoDB service
mongodb_service = MongoDBService()
