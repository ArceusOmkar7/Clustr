from fastapi import APIRouter
import time
from datetime import datetime
from app.db.mongodb import get_db

# Create a router for basic API endpoints
router = APIRouter()


@router.get("/")
async def home():
    """
    Root endpoint serving as a health check for the API.

    Returns:
    - A JSON response with server status, timestamp, and database connectivity check.
    """
    # Start time for response time calculation
    start_time = time.time()

    # Check database connectivity
    db_status = "connected"
    try:
        db = get_db()
        # Try a simple operation to verify connection is working
        server_info = db.client.server_info()
        db_version = server_info.get("version", "unknown")
    except Exception as e:
        db_status = f"error: {str(e)}"
        db_version = "unknown"

    # Calculate response time
    response_time = round((time.time() - start_time) *
                          1000, 2)  # Convert to milliseconds

    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "database": {
            "status": db_status,
            "version": db_version
        },
        "response_time": f"{response_time} ms"
    }
