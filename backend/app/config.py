from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    UPLOAD_FOLDER: str = "./uploads"
    ALLOWED_EXTENSIONS: set = {'png', 'jpg', 'jpeg', 'webp'}
    HOST: str = "127.0.0.1"
    PORT: int = 5000
    RELOAD: bool = True


settings = Settings()
