"""
Health check and status router.
"""

from fastapi import APIRouter
from ..models import HealthResponse
from ..services.correction import GrammarCorrectionService
from datetime import datetime

router = APIRouter(tags=["health"])

grammar_service = GrammarCorrectionService()


@router.get("/", response_model=dict)
async def root():
    """API root endpoint."""
    return {
        "message": "Text Correction API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/files/upload",
            "download_intermediate": "/files/download/{file_id}/intermediate",
            "download_final": "/files/download/{file_id}/final",
            "status": "/files/status/{file_id}",
            "health": "/health",
            "docs": "/docs"
        }
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        t5_available=grammar_service.is_available(),
        timestamp=datetime.now().isoformat()
    )
