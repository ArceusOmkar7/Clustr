# BLIP Image Captioning Container

This container provides a FastAPI service for generating captions for images using the BLIP (Bootstrapping Language-Image Pre-training) model from Salesforce.

## Features

- Single image captioning
- Batch image captioning
- Asynchronous batch processing
- GPU support (optional)
- Comprehensive error handling and logging

## API Endpoints

### Health Check
- `GET /`: Check if the service is running

### Single Image Captioning
- `POST /caption`: Generate a caption for a single image
  - Request body: `{"image_path": "/path/to/image.jpg"}`
  - Response: `{"image_path": "/path/to/image.jpg", "caption": "A person standing on a beach", "processing_time": 1.23}`

### Batch Image Captioning
- `POST /batch-caption`: Generate captions for multiple images
  - Request body: `{"image_paths": ["/path/to/image1.jpg", "/path/to/image2.jpg"]}`
  - Response: `{"results": [...], "total_processing_time": 2.45}`

### Asynchronous Batch Captioning
- `POST /async-batch-caption`: Process multiple images asynchronously
  - Request body: Same as batch-caption
  - Response: Same as batch-caption

## Building and Running

### CPU Version
```bash
# Build the container
docker build -t blip-captioning-cpu -f Dockerfile.cpu .

# Run the container
docker run -p 8000:8000 -v /path/to/images:/app/images blip-captioning-cpu
```

### GPU Version
```bash
# Build the container
docker build -t blip-captioning-gpu -f Dockerfile.gpu .

# Run the container
docker run --gpus all -p 8000:8000 -v /path/to/images:/app/images blip-captioning-gpu
```

## Usage Example

```python
import requests

# Single image captioning
response = requests.post(
    "http://localhost:8000/caption",
    json={"image_path": "/app/images/example.jpg"}
)
print(response.json())

# Batch captioning
response = requests.post(
    "http://localhost:8000/batch-caption",
    json={"image_paths": ["/app/images/example1.jpg", "/app/images/example2.jpg"]}
)
print(response.json())
```

## Notes

- The container expects image paths to be accessible from within the container
- For production use, consider:
  - Restricting CORS origins
  - Adding authentication
  - Implementing rate limiting
  - Using a proper logging system 