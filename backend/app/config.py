from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Use absolute path for uploads
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS: set = {'png', 'jpg', 'jpeg', 'webp'}
    HOST: str = "127.0.0.1"
    PORT: int = 5000
    RELOAD: bool = True
    UPLOAD_URL_PATH: str = "/uploads"  # Path to access uploaded files

    @property
    def BASE_URL(self) -> str:
        return f"http://{self.HOST}:{self.PORT}"


settings = Settings()
