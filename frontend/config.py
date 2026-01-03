"""
Frontend configuration.
"""

from pydantic_settings import BaseSettings


class FrontendSettings(BaseSettings):
    """Frontend settings."""
    
    app_title: str = "Text Correction Tool"
    app_icon: str = "✍️"
    api_url: str = "http://localhost:8000"
    
    # UI settings
    layout: str = "wide"
    sidebar_state: str = "expanded"
    
    class Config:
        env_prefix = "FRONTEND_"
        case_sensitive = False


settings = FrontendSettings()
