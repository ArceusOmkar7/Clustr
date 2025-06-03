from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import base, upload, ml, health
from app.config import settings
from app.db.mongodb import init_mongodb
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
# This ensures the application has a place to store uploaded files
Path(settings.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# Initialize the FastAPI application with metadata that appears in the docs
app = FastAPI(title="Clustr API", version="1.0.0")

# Initialize MongoDB
logger.info("Initializing MongoDB connection...")
try:
    mongodb_success = init_mongodb()
    if mongodb_success:
        logger.info("MongoDB connection successful")
    else:
        logger.warning(
            "Failed to connect to MongoDB - application will run with limited functionality")
except Exception as e:
    logger.error(f"Error initializing MongoDB: {str(e)}")
    logger.warning(
        "Application will run with limited functionality (no metadata storage)")

# Enable Cross-Origin Resource Sharing (CORS)
# This allows the frontend (running on a different domain/port) to communicate with the API
# In production, you would restrict this to specific origins instead of "*"
app.add_middleware(
    CORSMiddleware,
    # Allow requests from any origin (not secure for production)
    allow_origins=["*"],
    allow_credentials=True,  # Allow cookies to be included in requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers in requests
)

# Mount the uploads directory to serve static files
# This makes uploaded files accessible via HTTP at the specified URL path
# For example, a file "image.jpg" will be available at "/uploads/image.jpg"
app.mount(settings.UPLOAD_URL_PATH, StaticFiles(
    directory=settings.UPLOAD_FOLDER), name="uploads")

# Include routers to organize API endpoints
# base router: Basic endpoints like health check ("/")
# upload router: File upload endpoints ("/api/upload")
# ml router: Machine learning endpoints ("/api/ml")
# health router: Health check endpoints ("/api/health")
app.include_router(base.router)
app.include_router(upload.router, prefix="/api")
app.include_router(ml.router, prefix="/api/ml")
app.include_router(health.router, prefix="/api")
