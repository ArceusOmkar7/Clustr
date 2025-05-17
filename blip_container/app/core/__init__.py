# Core package initialization
from .config import (
    logger,
    UPLOAD_DIR,
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    CORS_ORIGINS,
    CORS_CREDENTIALS,
    CORS_METHODS,
    CORS_HEADERS
)
from .utils import process_image_background, validate_image_path

__all__ = [
    "logger",
    "UPLOAD_DIR",
    "API_TITLE",
    "API_DESCRIPTION",
    "API_VERSION",
    "CORS_ORIGINS",
    "CORS_CREDENTIALS",
    "CORS_METHODS",
    "CORS_HEADERS",
    "process_image_background",
    "validate_image_path"
]
