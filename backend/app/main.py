from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import base, upload
from app.config import settings
from pathlib import Path

# Create uploads directory if it doesn't exist
Path(settings.UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Clustr API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(base.router)
app.include_router(upload.router, prefix="/api")
