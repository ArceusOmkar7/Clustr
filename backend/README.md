# Clustr Backend

This is the backend API for the Clustr application, built with FastAPI. It provides a robust and performant system for handling file uploads, particularly optimized for image files.

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs with automatic OpenAPI documentation
- **Pydantic**: Data validation and settings management using Python type annotations
- **Uvicorn**: ASGI server for running the application with high performance
- **Python 3.8+**: Modern Python features including type hints and async/await syntax
- **python-multipart**: Library for handling file uploads with multipart/form-data
- **python-dotenv**: For environment-based configuration

## Project Structure

```
backend/
├── app/                     # Application package
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Application configuration settings
│   ├── main.py              # FastAPI application setup and entry point
│   ├── models/              # Pydantic models for request/response data
│   │   ├── __init__.py
│   │   └── upload_models.py # Models for file upload functionality
│   ├── routers/             # API route definitions
│   │   ├── __init__.py
│   │   ├── base.py          # Base routes (health check, etc.)
│   │   └── upload.py        # File upload routes
│   ├── services/            # Business logic implementation
│   │   ├── __init__.py
│   │   └── upload_service.py # Upload service implementation
│   └── utils/               # Helper functions
│       ├── __init__.py
│       └── helpers.py       # Utility functions (file validation, error handling)
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

### Routers (app/routers/)

The API is organized into logical router modules:

- **base.py**: Basic routes for health checks and application status
  - `GET /`: Simple health check endpoint returning a "Hello World" message

- **upload.py**: File upload functionality
  - `POST /api/upload`: Endpoint for uploading one or more files
    - Accepts multipart/form-data with one or more files
    - Returns UploadSuccess with metadata about uploaded files

### Services (app/services/)

Service modules contain the business logic:

- **upload_service.py**: Handles file upload processing
  - Validates file types against allowed extensions
  - Securely saves files to the upload directory
  - Generates preview URLs
  - Returns structured metadata about the uploaded files

### Utils (app/utils/)

Utility functions shared across the application:

- **helpers.py**: Contains helper functions
  - `send_error()`: Standardized error response generation
  - `allowed_file()`: File extension validation against allowed types

## API Endpoints

### Base API

- **GET /**: Health check endpoint
  - Response: `{"message": "Hello World"}`

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
  - Error responses:
    - 406 Not Acceptable: When no files are found in the request
    - 415 Unsupported Media Type: When file type is not allowed

## Configuration

Configuration is managed through the `app/config.py` file using Pydantic's BaseSettings. This provides type validation and automatic loading from environment variables.

### Settings

- `BASE_DIR`: Base directory of the application
- `UPLOAD_FOLDER`: Directory for storing uploaded files (default: `<BASE_DIR>/uploads`)
- `ALLOWED_EXTENSIONS`: Set of allowed file extensions (default: 'png', 'jpg', 'jpeg', 'webp')
- `HOST`: Host address (default: '127.0.0.1')
- `PORT`: Port number (default: 5000)
- `RELOAD`: Auto-reload on code changes (default: True, ideal for development)
- `UPLOAD_URL_PATH`: URL path to access uploaded files (default: '/uploads')
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
```

## File Upload Service Implementation

The file upload service (`app/services/upload_service.py`) handles the upload process:

1. **Validation**: Checks if the file extensions are allowed using the `allowed_file()` utility function
2. **Storage**: Securely saves files to the configured upload directory
3. **URL Generation**: Creates preview URLs for accessing the files
4. **Response Creation**: Returns metadata about each successfully uploaded file

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