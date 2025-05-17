import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create uploads directory for storing temporary image files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# API metadata
API_TITLE = "BLIP Image Captioning API"
API_DESCRIPTION = "API for generating captions for images using the BLIP model"
API_VERSION = "1.0.0"

# CORS settings
CORS_ORIGINS = ["*"]  # In production, replace with specific origins
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]
