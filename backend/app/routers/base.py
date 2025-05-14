from fastapi import APIRouter

# Create a router for basic API endpoints
router = APIRouter()


@router.get("/")
async def home():
    """
    Root endpoint serving as a simple health check for the API.

    Returns:
    - A simple JSON response with a "Hello World" message to indicate the API is running.

    This endpoint can be used to:
    1. Check if the API is accessible
    2. Verify the server is running correctly
    3. Test basic connectivity
    """
    return {"message": "Hello World"}
