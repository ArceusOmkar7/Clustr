from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import time
import httpx
from datetime import datetime
from app.db.mongodb import get_db
from app.config import settings
from app.services.mongodb_service import mongodb_service
import logging

logger = logging.getLogger(__name__)

# Create a router for health check endpoints
router = APIRouter()


async def check_captioner_health():
    """Check if the BLIP captioner service is healthy."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.BLIP_BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "url": settings.BLIP_BASE_URL,
                    "response_time": data.get("response_time", "unknown"),
                    "version": data.get("version", "unknown")
                }
            else:
                return {
                    "status": "unhealthy",
                    "url": settings.BLIP_BASE_URL,
                    "error": f"HTTP {response.status_code}"
                }
    except httpx.RequestError as e:
        return {
            "status": "unreachable",
            "url": settings.BLIP_BASE_URL,
            "error": str(e)
        }
    except Exception as e:
        return {
            "status": "error",
            "url": settings.BLIP_BASE_URL,
            "error": str(e)
        }


@router.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint for the API and its dependencies.

    Returns:
    - JSON response with status of backend, database, and captioner service
    """
    start_time = time.time()

    # Check database connectivity
    db_status = "connected"
    db_info = {}
    try:
        db = get_db()
        server_info = db.client.server_info()
        db_info = {
            "status": "connected",
            "version": server_info.get("version", "unknown"),
            "host": settings.MONGODB_URL.split("@")[-1].split("/")[0] if "@" in settings.MONGODB_URL else "local"
        }        # Get some statistics
        try:
            stats = mongodb_service.get_caption_statistics()
            db_info["image_count"] = stats.get("total_images", 0)
        except Exception as stats_error:
            logger.warning(f"Could not get statistics: {stats_error}")
            db_info["image_count"] = 0

    except Exception as e:
        db_info = {
            "status": "error",
            "error": str(e)
        }

    # Check captioner service
    captioner_info = await check_captioner_health()

    # Calculate response time
    response_time = round((time.time() - start_time) * 1000, 2)

    # Determine overall health
    overall_status = "healthy"
    if db_info["status"] != "connected":
        overall_status = "degraded"
    if captioner_info["status"] not in ["healthy"]:
        overall_status = "degraded" if overall_status == "healthy" else "critical"

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "response_time": f"{response_time} ms",
        "services": {
            "backend": {
                "status": "online",
                "version": "1.0.0"
            },
            "database": db_info,
            "captioner": captioner_info
        }
    }


@router.get("/health/page", response_class=HTMLResponse)
async def health_check_page():
    """
    HTML health check page showing the status of all services.
    """
    health_data = await health_check()

    # Determine status colors
    def get_status_color(status):
        if status in ["healthy", "online", "connected"]:
            return "#22c55e"  # green
        elif status in ["degraded", "unhealthy"]:
            return "#f59e0b"  # amber
        else:
            return "#ef4444"  # red

    # Create HTML response
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Clustr Backend Health Check</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f8fafc;
                line-height: 1.6;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .status-card {{
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                margin: 15px 0;
                overflow: hidden;
            }}
            .status-header {{
                padding: 12px 16px;
                font-weight: 600;
                border-bottom: 1px solid #e2e8f0;
            }}
            .status-body {{
                padding: 16px;
            }}
            .status-indicator {{
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 8px;
            }}
            .meta-info {{
                color: #64748b;
                font-size: 14px;
                margin-top: 10px;
            }}
            .refresh-btn {{
                background: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                margin: 10px 0;
            }}
            .refresh-btn:hover {{
                background: #2563eb;
            }}
            .error-text {{
                color: #dc2626;
                font-size: 14px;
                margin-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔧 Clustr Backend Health Check</h1>
                <p>System Status Dashboard</p>
            </div>
            <div class="content">
                <div class="status-card">
                    <div class="status-header">
                        <span class="status-indicator" style="background-color: {get_status_color(health_data['status'])}"></span>
                        Overall Status: <strong>{health_data['status'].title()}</strong>
                    </div>
                    <div class="status-body">
                        <div class="meta-info">
                            <strong>Last Updated:</strong> {health_data['timestamp']}<br>
                            <strong>Response Time:</strong> {health_data['response_time']}
                        </div>
                        <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh</button>
                    </div>
                </div>
                
                <div class="status-card">
                    <div class="status-header">
                        <span class="status-indicator" style="background-color: {get_status_color(health_data['services']['backend']['status'])}"></span>
                        Backend Service
                    </div>
                    <div class="status-body">
                        <strong>Status:</strong> {health_data['services']['backend']['status'].title()}<br>
                        <strong>Version:</strong> {health_data['services']['backend']['version']}
                    </div>
                </div>
                
                <div class="status-card">
                    <div class="status-header">
                        <span class="status-indicator" style="background-color: {get_status_color(health_data['services']['database']['status'])}"></span>
                        Database Service
                    </div>
                    <div class="status-body">
                        <strong>Status:</strong> {health_data['services']['database']['status'].title()}<br>
                        {'<strong>Version:</strong> ' + health_data['services']['database'].get('version', 'unknown') + '<br>' if 'version' in health_data['services']['database'] else ''}
                        {'<strong>Host:</strong> ' + health_data['services']['database'].get('host', 'unknown') + '<br>' if 'host' in health_data['services']['database'] else ''}
                        {'<strong>Image Count:</strong> ' + str(health_data['services']['database'].get('image_count', 0)) + '<br>' if 'image_count' in health_data['services']['database'] else ''}
                        {'<div class="error-text">Error: ' + health_data['services']['database'].get('error', '') + '</div>' if 'error' in health_data['services']['database'] else ''}
                    </div>
                </div>
                
                <div class="status-card">
                    <div class="status-header">
                        <span class="status-indicator" style="background-color: {get_status_color(health_data['services']['captioner']['status'])}"></span>
                        BLIP Captioner Service
                    </div>
                    <div class="status-body">
                        <strong>Status:</strong> {health_data['services']['captioner']['status'].title()}<br>
                        <strong>URL:</strong> {health_data['services']['captioner']['url']}<br>
                        {'<strong>Response Time:</strong> ' + str(health_data['services']['captioner'].get('response_time', 'unknown')) + '<br>' if 'response_time' in health_data['services']['captioner'] else ''}
                        {'<strong>Version:</strong> ' + str(health_data['services']['captioner'].get('version', 'unknown')) + '<br>' if 'version' in health_data['services']['captioner'] else ''}
                        {'<div class="error-text">Error: ' + health_data['services']['captioner'].get('error', '') + '</div>' if 'error' in health_data['services']['captioner'] else ''}
                    </div>
                </div>
                
                <div class="meta-info" style="text-align: center; margin-top: 30px;">
                    <p>This page automatically refreshes data when you reload it.<br>
                    For real-time monitoring, consider setting up automated health checks.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@router.get("/health/captioner")
async def captioner_health():
    """Check only the captioner service health."""
    return await check_captioner_health()


@router.get("/health/database")
async def database_health():
    """Check only the database health."""
    try:
        db = get_db()
        server_info = db.client.server_info()
        stats = mongodb_service.get_caption_statistics()
        
        return {
            "status": "connected",
            "version": server_info.get("version", "unknown"),
            "host": settings.MONGODB_URL.split("@")[-1].split("/")[0] if "@" in settings.MONGODB_URL else "local",
            "image_count": stats.get("total_images", 0),
            "captioned_images": stats.get("captioned", 0),
            "uncaptioned_images": stats.get("uncaptioned", 0)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
