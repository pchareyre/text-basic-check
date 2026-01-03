"""
Main FastAPI application.

This module sets up the FastAPI application with proper architecture:
- Configuration management
- Router registration
- Middleware setup
- CORS configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import health, files

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Offline text correction using SymSpell and T5-ONNX",
    version=settings.app_version
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Register routers
app.include_router(health.router)
app.include_router(files.router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"API will be available at http://{settings.api_host}:{settings.api_port}")
    print(f"Docs available at http://{settings.api_host}:{settings.api_port}/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print(f"Shutting down {settings.app_name}")
