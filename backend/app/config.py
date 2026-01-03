"""
Application configuration settings.
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    # API settings
    app_name: str = "Text Correction API"
    app_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS settings
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # Model settings
    t5_model_dir: str = "t5-small-onnx-q"
    enable_t5_by_default: bool = True
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    allowed_extensions: list = [".txt"]
    temp_dir: Path = Path("/tmp/text_correction")
    
    # Spell checker settings
    spell_checker_language: str = "en"
    
    class Config:
        env_prefix = "APP_"
        case_sensitive = False


settings = Settings()
