"""
BLIP Image Captioning API
-------------------------
This FastAPI application provides endpoints for generating captions for images using the BLIP model.
It includes both a REST API and a web interface for testing.
"""

import uvicorn
from .api import create_app

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
