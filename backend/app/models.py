"""
Data models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UploadResponse(BaseModel):
    """Response model for file upload."""
    file_id: str
    original_filename: str
    status: str
    message: str
    t5_enabled: bool
    t5_applied: bool
    intermediate_corrections: int
    final_corrections: int


class FileMetadata(BaseModel):
    """File metadata model."""
    file_id: str
    original_filename: str
    original_path: str
    intermediate_path: str
    final_path: str
    timestamp: str
    t5_applied: bool = False


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    t5_available: bool
    timestamp: str


class StatusResponse(BaseModel):
    """File status response."""
    file_id: str
    status: str
    metadata: dict
