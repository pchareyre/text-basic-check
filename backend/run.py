"""
Backend entry point.

Run this script to start the API server:
    python -m backend.run
    
Or with uvicorn directly:
    uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
"""

import uvicorn
from .app.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    )
