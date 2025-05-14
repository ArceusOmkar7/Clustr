import uvicorn
from app.main import app
from app.config import settings

if __name__ == "__main__":
    # This is the entry point of the application when running directly
    # Using uvicorn to serve the FastAPI application defined in app.main
    # Configuration is loaded from settings in app.config
    uvicorn.run(
        "app.main:app",  # Path to the FastAPI app object
        host=settings.HOST,  # Host address from settings
        port=settings.PORT,  # Port number from settings
        # Auto-reload on code changes (useful for development)
        reload=settings.RELOAD
    )
