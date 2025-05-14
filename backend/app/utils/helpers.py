from fastapi import HTTPException
from app.config import settings


def send_error(message: str, status_code: int):
    """
    Standardized way to raise an HTTP exception with an error message.

    This provides a consistent error response structure across the API.
    When called, it will stop execution and return an error response to the client.

    Parameters:
    - message: The error message to display to the client
    - status_code: HTTP status code to return (e.g., 400, 404, 500)

    Example response:
    {
        "detail": "No files found in request"
    }
    """
    raise HTTPException(status_code=status_code, detail=message)


def allowed_file(filename: str) -> bool:
    """
    Check if a file has an allowed extension.

    This is a security measure to prevent uploading of potentially dangerous files
    by restricting uploads to known, safe file types defined in the settings.

    Parameters:
    - filename: The name of the file to check

    Returns:
    - True if the file extension is in the ALLOWED_EXTENSIONS set, False otherwise

    Example:
    - allowed_file("image.jpg") -> True
    - allowed_file("script.php") -> False (assuming php is not in ALLOWED_EXTENSIONS)
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS
