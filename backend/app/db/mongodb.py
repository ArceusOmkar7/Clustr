from pymongo import MongoClient
from app.config import settings
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Initialize MongoDB client
client = None
db = None


def init_mongodb():
    """
    Initialize MongoDB connection.
    This function should be called when the application starts.
    """
    global client, db

    try:
        client = MongoClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_DATABASE]

        # Print MongoDB server information to verify connection
        server_info = client.server_info()
        logger.info(
            f"Connected to MongoDB version: {server_info.get('version', 'unknown')}")

        # Ensure the required collections exist
        if settings.MONGODB_UPLOADS_COLLECTION not in db.list_collection_names():
            db.create_collection(settings.MONGODB_UPLOADS_COLLECTION)
            logger.info(
                f"Created collection: {settings.MONGODB_UPLOADS_COLLECTION}")

        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        return False


def get_db():
    """
    Get the database instance.

    Returns:
        The MongoDB database instance
    """
    if db is None:
        init_mongodb()
    return db


def get_collection(collection_name):
    """
    Get a collection from the database.

    Args:
        collection_name: Name of the collection

    Returns:
        The MongoDB collection
    """
    database = get_db()
    return database[collection_name]
