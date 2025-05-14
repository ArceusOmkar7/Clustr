from fastapi import HTTPException
from app.config import settings


def send_error(message: str, status_code: int):
    raise HTTPException(status_code=status_code, detail=message)


def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS
