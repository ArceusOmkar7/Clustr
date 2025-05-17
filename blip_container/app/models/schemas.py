from pydantic import BaseModel
from typing import List


class CaptionRequest(BaseModel):
    """Request model for single image captioning."""
    image_path: str


class CaptionResponse(BaseModel):
    """Response model containing caption and metadata."""
    image_path: str
    caption: str
    processing_time: float


class BatchCaptionRequest(BaseModel):
    """Request model for batch image captioning."""
    image_paths: List[str]


class BatchCaptionResponse(BaseModel):
    """Response model for batch captioning results."""
    results: List[CaptionResponse]
    total_processing_time: float
