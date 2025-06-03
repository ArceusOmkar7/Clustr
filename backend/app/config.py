from pydantic_settings import BaseSettings
import os
from typing import Set


class Settings(BaseSettings):
    """
    Application configuration settings.

    Pydantic's BaseSettings automatically loads values from environment variables.
    The values defined here are just defaults used when the corresponding
    environment variables are not set.

    Environment variables take precedence in this order:
    1. Actual environment variables (set in the OS)
    2. Variables from .env file
    3. Default values defined here
    """

    # Use absolute path for uploads - calculates the parent directory of the current file
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Where uploaded files will be stored - defaults to an 'uploads' folder in the project root
    UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads")

    # File extensions that are allowed to be uploaded
    # Security: restricts uploads to only image files with these extensions
    ALLOWED_EXTENSIONS: Set[str] = {
        'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff', 'tif'
    }

    # Server configuration (will be overridden by environment variables if set)
    HOST: str = "127.0.0.1"
    PORT: int = 5000
    RELOAD: bool = True

    # URL path where uploads can be accessed
    UPLOAD_URL_PATH: str = "/uploads"

    # MongoDB configuration (will be overridden by environment variables if set)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "clustr"
    MONGODB_UPLOADS_COLLECTION: str = "uploads"

    # BLIP Captioning Service Base URL
    BLIP_BASE_URL: str = "http://localhost:8000"

    @property
    def BASE_URL(self) -> str:
        """
        Computed property that returns the full base URL of the application.
        Used for generating complete URLs to access uploaded files.
        """
        return f"http://{self.HOST}:{self.PORT}"

    class Config:
        # Load .env file from the backend directory
        env_file = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), ".env")
        env_file_encoding = "utf-8"

        # Allow environment variables to be case-insensitive
        case_sensitive = False


# Create a global settings instance that can be imported throughout the application
# This will automatically load values from environment variables and .env file
settings = Settings()
