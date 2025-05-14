from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """
    Application configuration settings.

    Using Pydantic's BaseSettings allows:
    1. Environment variable overrides (set HOST=0.0.0.0 to change the host)
    2. Type validation (PORT must be an integer)
    3. Default values if not specified elsewhere
    """

    # Use absolute path for uploads - calculates the parent directory of the current file
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Where uploaded files will be stored - defaults to an 'uploads' folder in the project root
    UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads")

    # File extensions that are allowed to be uploaded
    # Security: restricts uploads to only image files with these extensions
    ALLOWED_EXTENSIONS: set = {'png', 'jpg', 'jpeg', 'webp'}

    # Server configuration
    HOST: str = "127.0.0.1"  # Default to localhost
    PORT: int = 5000         # Default port for the server
    RELOAD: bool = True      # Auto-reload on code changes (for development)

    # URL path where uploads can be accessed, e.g., http://127.0.0.1:5000/uploads/image.jpg
    UPLOAD_URL_PATH: str = "/uploads"

    @property
    def BASE_URL(self) -> str:
        """
        Computed property that returns the full base URL of the application.
        Used for generating complete URLs to access uploaded files.
        """
        return f"http://{self.HOST}:{self.PORT}"


# Create a global settings instance that can be imported throughout the application
settings = Settings()
