# Clustr Backend

This is the backend API for the Clustr application, built with FastAPI. It provides a robust and performant system for handling file uploads, particularly optimized for image files.

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs with automatic OpenAPI documentation
- **Pydantic**: Data validation and settings management using Python type annotations
- **Uvicorn**: ASGI server for running the application with high performance
- **Python 3.8+**: Modern Python features including type hints and async/await syntax
- **python-multipart**: Library for handling file uploads with multipart/form-data
- **python-dotenv**: For environment-based configuration
- **MongoDB**: NoSQL database for storing metadata about uploaded files
- **Pillow**: Python Imaging Library for processing image files and extracting metadata

## Project Structure

```
backend/
├── app/                     # Application package
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Application configuration settings
│   ├── main.py              # FastAPI application setup and entry point
│   ├── db/                  # Database connection modules
│   │   ├── __init__.py
│   │   └── mongodb.py       # MongoDB initialization and connection
│   ├── models/              # Pydantic models for request/response data
│   │   ├── __init__.py
│   │   └── upload_models.py # Models for file upload functionality
│   ├── routers/             # API route definitions
│   │   ├── __init__.py
│   │   ├── base.py          # Base routes (health check, etc.)
│   │   └── upload.py        # File upload routes
│   ├── services/            # Business logic implementation
│   │   ├── __init__.py
│   │   ├── mongodb_service.py # MongoDB service implementation
│   │   └── upload_service.py  # Upload service implementation
│   ├── ml/                  # Machine learning services
│   │   ├── __init__.py
│   │   └── caption_service.py # Image captioning and tagging service
│   └── utils/               # Helper functions
│       ├── __init__.py
│       ├── helpers.py       # Utility functions (file validation, error handling)
│       └── image_utils.py   # Image processing utilities (dimensions extraction)
├── uploads/                 # Directory for storing uploaded files
├── requirements.txt         # Project dependencies
└── run.py                   # Entry point to run the application
```

## Detailed Component Breakdown

### Models (app/models/)

The application uses Pydantic models for request and response validation:

- **UploadResponse**: Represents a single uploaded file with metadata
  - `stored_filename`: Name of the file as stored on the server
  - `preview_url`: URL to access the uploaded file
  - `original_filename`: Original name of the uploaded file
  - `file_size`: Size of the file in bytes
  - `content_type`: MIME type of the file (optional)

- **UploadSuccess**: Response model for successful uploads
  - `message`: Success message
  - `data`: List of UploadResponse objects for each uploaded file

- **DBUploadModel**: Model for storing file metadata in MongoDB
  - `id`: Unique identifier for the file
  - `original_name`: Original filename
  - `filename`: Stored filename
  - `file_path`: Local path where the file is stored
  - `url`: Complete URL to access the file
  - `upload_time`: When the file was uploaded
  - `size`: File size in bytes
  - `dimensions`: Image dimensions (width and height)
  - `status`: Processing status (pending/processed/error)
  - `caption`: Optional caption for the image
  - `tags`: List of tags associated with the image
  - `faces`: Information about detected faces
  - `face_cluster_ids`: IDs of face clusters

### Routers (app/routers/)

The API is organized into logical router modules:

- **base.py**: Basic routes for health checks and application status
  - `GET /`: Health check endpoint returning server status and database connectivity

- **upload.py**: File upload functionality
  - `POST /api/upload`: Endpoint for uploading one or more files
    - Accepts multipart/form-data with one or more files
    - Returns UploadSuccess with metadata about uploaded files
  - `GET /api/uploads`: Retrieves metadata for all uploaded files
  - `GET /api/uploads/{file_id}`: Retrieves metadata for a specific file
  - `GET /api/debug/dimensions`: Debug endpoint to check image dimension extraction

### Services (app/services/)

Service modules contain the business logic:

- **upload_service.py**: Handles file upload processing
  - Validates file types against allowed extensions
  - Securely saves files to the upload directory
  - Extracts image dimensions
  - Stores metadata in MongoDB
  - Generates preview URLs
  - Returns structured metadata about the uploaded files

- **mongodb_service.py**: Handles database operations
  - Provides methods to save, retrieve, and query file metadata
  - Error handling for database operations

### ML Services (app/ml/)

Machine learning and AI-powered services:

- **caption_service.py**: Integrates with BLIP Captioner service for AI-powered image analysis
  - Generates captions and tags for uploaded images
  - Supports both individual caption/tag retrieval and combined operations
  - Handles background processing of images through BLIP service
  - Updates database with generated captions and tags
  - Error handling for ML service failures
  - Stores metadata in MongoDB
  - Generates preview URLs
  - Returns structured metadata about the uploaded files

- **mongodb_service.py**: Handles database operations
  - Provides methods to save, retrieve, and query file metadata
  - Error handling for database operations

### Utils (app/utils/)

Utility functions shared across the application:

- **helpers.py**: Contains helper functions
  - `send_error()`: Standardized error response generation
  - `allowed_file()`: File extension validation against allowed types

- **image_utils.py**: Image processing utilities
  - `get_image_dimensions()`: Extracts dimensions from image files

## API Endpoints

### Base API

- **GET /**: Health check endpoint
  - Response: Server status, timestamp, and database connectivity information

### Upload API

- **POST /api/upload**: Upload one or more files
  - Request: 
    - Content-Type: `multipart/form-data`
    - Body: One or more files with the name "files"
  - Response:
    ```json
    {
      "message": "Successfully uploaded 2 files",
      "data": [
        {
          "stored_filename": "image1.jpg",
          "preview_url": "http://127.0.0.1:5000/uploads/image1.jpg",
          "original_filename": "image1.jpg",
          "file_size": 125000,
          "content_type": "image/jpeg"
        },
        {
          "stored_filename": "image2.png",
          "preview_url": "http://127.0.0.1:5000/uploads/image2.png",
          "original_filename": "image2.png",
          "file_size": 250000,
          "content_type": "image/png"
        }
      ]
    }
    ```

- **GET /api/uploads**: Get paginated uploads
  - Query Parameters:
    - `page`: Page number (1-indexed, default 1)
    - `limit`: Number of items per page (default 20, max 100)
  - Response:
    ```json
    {
      "data": [
        {
          "id": "60d21b4967d0d8992e610c85",
          "original_name": "vacation.jpg",
          "filename": "60d21b4967d0d8992e610c85.jpg",
          "file_path": "/uploads/images/60d21b4967d0d8992e610c85.jpg",
          "url": "http://example.com/uploads/images/60d21b4967d0d8992e610c85.jpg",
          "upload_time": "2023-08-01",
          "size": 1024000,
          "dimensions": {
            "width": 1920,
            "height": 1080
          },
          "status": "pending",
          "caption": "Beach vacation",
          "tags": [],
          "faces": [],
          "face_cluster_ids": []
        },
        // ... more items ...
      ],
      "total": 42,
      "page": 1,
      "limit": 20
    }
    ```

- **GET /api/uploads/{file_id}**: Get metadata for a specific file
  - Returns the complete metadata for a specific file by its ID

## BLIP Service Integration

The Clustr backend integrates with the BLIP Captioner service to provide AI-powered image captioning and tagging functionality. This service analyzes uploaded images and generates both descriptive captions and relevant tags.

### Caption Service Features

The `app/ml/caption_service.py` module provides the following functionality:

- **Automatic Caption Generation**: Uses BLIP-2 model to generate descriptive captions for uploaded images
- **Tag Generation**: Extracts relevant tags that describe the content, objects, and scenes in images
- **Background Processing**: Handles image analysis asynchronously to avoid blocking upload operations
- **Database Integration**: Automatically updates MongoDB with generated captions and tags

### Available Functions

- `generate_caption_and_update_db(image_id, image_path)`: Sends image to BLIP service and updates database with both caption and tags
- `get_image_caption(image_id)`: Retrieves caption for a specific image (generates if not available)
- `get_image_tags(image_id)`: Retrieves tags for a specific image (generates if not available)
- `get_image_caption_and_tags(image_id)`: Retrieves both caption and tags in a single operation

### BLIP Service Requirements

To use the caption and tagging functionality, you need to have the BLIP Captioner service running:

1. **BLIP Service URL**: Configure the `BLIP_SERVICE_URL` environment variable to point to your BLIP service instance
2. **Service Response Format**: The BLIP service should return JSON responses with the following structure:
   ```json
   {
     "caption": "A descriptive caption of the image",
     "tags": ["tag1", "tag2", "tag3", ...]
   }
   ```

### Usage Example

The caption service is automatically triggered during the upload process. Images are processed in the background, and their metadata is updated with captions and tags. You can also manually retrieve this information:

```python
from app.ml.caption_service import get_image_caption_and_tags

# Get both caption and tags for an image
result = await get_image_caption_and_tags("image_id_here")
print(f"Caption: {result['caption']}")
print(f"Tags: {result['tags']}")
```

### Error Handling

The caption service includes robust error handling:
- Network failures when connecting to BLIP service
- Invalid image formats or corrupted files
- Service timeouts and response validation
- Graceful degradation when ML services are unavailable

## Configuration

Configuration is managed through the `app/config.py` file using Pydantic's BaseSettings. This provides type validation and automatic loading from environment variables.

### Settings

- `BASE_DIR`: Base directory of the application
- `UPLOAD_FOLDER`: Directory for storing uploaded files (default: `<BASE_DIR>/uploads`)
- `ALLOWED_EXTENSIONS`: Set of allowed file extensions (default: 'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff', 'tif')
- `HOST`: Host address (default: '127.0.0.1')
- `PORT`: Port number (default: 5000)
- `RELOAD`: Auto-reload on code changes (default: True, ideal for development)
- `UPLOAD_URL_PATH`: URL path to access uploaded files (default: '/uploads')
- `MONGODB_URL`: MongoDB connection string (default: 'mongodb://localhost:27017')
- `MONGODB_DATABASE`: MongoDB database name (default: 'clustr')
- `MONGODB_UPLOADS_COLLECTION`: MongoDB collection for uploads (default: 'uploads')
- `BLIP_SERVICE_URL`: URL for the BLIP Captioner service (default: 'http://localhost:8001')
- `BASE_URL`: Computed property that returns the full base URL of the application

### Environment Variables

The configuration can be overridden using environment variables. Create a `.env` file in the project root:

```env
# Server settings
HOST=0.0.0.0  # Listen on all interfaces
PORT=8000     # Custom port
RELOAD=False  # Disable auto-reload in production

# Storage settings
UPLOAD_FOLDER=/path/to/custom/storage

# MongoDB configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=clustr
MONGODB_UPLOADS_COLLECTION=uploads

# BLIP Service configuration
BLIP_SERVICE_URL=http://localhost:8001
```

## File Upload Service Implementation

The file upload service (`app/services/upload_service.py`) handles the upload process:

1. **Validation**: Checks if the file extensions are allowed using the `allowed_file()` utility function
2. **Storage**: Securely saves files to the configured upload directory
3. **Metadata Extraction**: Extracts image dimensions and other metadata using Pillow
4. **MongoDB Storage**: Stores file metadata in MongoDB for later retrieval
5. **URL Generation**: Creates preview URLs for accessing the files
6. **Response Creation**: Returns metadata about each successfully uploaded file

### Security Considerations

- The service validates file types to prevent uploading of potentially malicious files
- In a production environment, consider implementing:
  - File size limitations
  - Rate limiting
  - Authentication for upload endpoints
  - Additional validation like content type checking
  - Virus/malware scanning of uploaded files

## Error Handling

The application uses FastAPI's exception handling with custom error responses:

- HTTP exceptions are raised using the `send_error()` utility function
- This ensures consistent error formats across the API

## CORS Configuration

Cross-Origin Resource Sharing (CORS) is configured in `main.py` to allow requests from all origins. This is suitable for development but should be restricted in production.

## File Storage

Uploaded files are stored in the `uploads/` directory and served as static files through FastAPI's StaticFiles mounting. In production, consider:

- Using a CDN for serving static files
- Implementing cloud storage (S3, GCP Storage, etc.)
- Setting up proper file permissions and backup strategies

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (venv, virtualenv, or conda)
- MongoDB instance (local or remote)
- BLIP Captioner service (for AI-powered captions and tags)

### External Service Dependencies

**BLIP Captioner Service**: The application integrates with a separate BLIP service for AI-powered image analysis. This service should be running and accessible at the configured URL before using caption/tag functionality.

- Repository: [BLIP Captioner](https://github.com/yourusername/BLIP-Captioner)
- Default URL: http://localhost:8001
- Required endpoints: `/caption` (POST) for image analysis

### Installation

1. Clone the repository
2. Navigate to the backend directory
3. Create a virtual environment:
   ```
   python -m venv .venv
   ```
4. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

Run the application using:

```
python run.py
```

The API will be available at http://127.0.0.1:5000

### API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: http://127.0.0.1:5000/docs
- ReDoc: http://127.0.0.1:5000/redoc

These interfaces allow you to:
- Read the API documentation
- Try out the API endpoints directly from your browser
- See request and response schemas

## Development

### Adding New Endpoints

1. Create a new router or extend an existing one in `app/routers/`
2. Define Pydantic models in `app/models/` for request/response validation
3. Implement business logic in `app/services/`
4. Register the router in `app/main.py`

### Code Style

The project follows PEP 8 guidelines for Python code style.

## Production Deployment

For deploying to production, consider:

1. Using a process manager (Gunicorn, Supervisor)
2. Setting up reverse proxy (Nginx, Apache)
3. Implementing proper logging
4. Setting up monitoring
5. Restricting CORS to specific origins
6. Using environment variables for configuration

Example Gunicorn configuration:

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /uploads {
        alias /path/to/uploads;
        expires 1d;
        add_header Cache-Control "public";
    }
}
```

## Logging

To implement proper logging, modify `main.py` to set up loggers for the application.

## Testing

To implement testing:

1. Create a `tests` directory
2. Use pytest for testing
3. Write unit tests for services and utilities
4. Write integration tests for API endpoints

## Future Enhancements

Potential improvements for the application:

1. Authentication and authorization
2. File size limits and validation
3. Image processing (resizing, optimization)
4. Asynchronous processing for large files
5. Cloud storage integration
6. File deletion and management APIs
7. Face detection and clustering enhancements
8. Advanced image search capabilities using generated tags
9. Batch processing for multiple images
10. Custom ML model integration beyond BLIP

## MongoDB Integration

The application uses MongoDB to store metadata about uploaded files. This includes:

1. **File Information**: Original filename, stored filename, file path, URL, etc.
2. **Image Metadata**: Dimensions, size, and content type
3. **Processing Status**: Status of any image processing (pending, processed, error)
4. **AI-Generated Content**: Captions and tags generated by the BLIP service
5. **Custom Metadata**: Face detection data, cluster IDs, and other analysis results

### MongoDB Service

The `mongodb_service.py` provides an interface for interacting with MongoDB:

- `save_upload_metadata()`: Saves file metadata to MongoDB
- `get_upload_metadata()`: Retrieves metadata for a specific file
- `get_all_uploads()`: Retrieves metadata for all uploaded files
- Database operations for updating captions, tags, and processing status

### Image Dimensions Extraction

The application extracts dimensions from uploaded images using the Pillow library:

1. When a file is uploaded, it's saved to the uploads directory
2. The `get_image_dimensions()` function opens the image and extracts its dimensions
3. The dimensions are stored in the MongoDB metadata
4. This information can be used for image processing, thumbnails, or display purposes

The application extracts image dimensions using the Pillow library, which has native support for these formats:
- PNG (.png)
- JPEG (.jpg, .jpeg)
- WebP (.webp)
- BMP (.bmp)
- TIFF (.tiff, .tif)

These formats were chosen because they are widely used and have robust support in Pillow without requiring additional plugins.

## MongoDB Setup

This application uses MongoDB to store metadata about uploaded files. Make sure you have MongoDB installed and running on your system.

### Installing MongoDB

- **Windows**: Download and install from [MongoDB website](https://www.mongodb.com/try/download/community)
- **macOS**: `brew install mongodb-community`
- **Linux**: Refer to your distribution's package manager

### Running MongoDB

- **Windows**: MongoDB should run as a service after installation
- **macOS**: `brew services start mongodb-community`
- **Linux**: `sudo systemctl start mongod`

The application will automatically create the necessary database and collections on startup. 