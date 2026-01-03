"""
API client for communicating with backend.
"""

import requests
from typing import Optional, Tuple
from ..config import settings


class APIClient:
    """Client for backend API communication."""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize API client."""
        self.base_url = base_url or settings.api_url
    
    def check_health(self) -> bool:
        """Check if API is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        enable_t5: bool = True
    ) -> Optional[dict]:
        """Upload file to API for correction."""
        files = {"file": (filename, file_content, "text/plain")}
        params = {"enable_t5": enable_t5}
        
        try:
            response = requests.post(
                f"{self.base_url}/files/upload",
                files=files,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error uploading file: {e}")
            return None
    
    def download_file(
        self,
        file_id: str,
        file_type: str
    ) -> Optional[bytes]:
        """Download file from API."""
        try:
            response = requests.get(
                f"{self.base_url}/files/download/{file_id}/{file_type}"
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")
            return None
    
    def get_status(self, file_id: str) -> Optional[dict]:
        """Get file processing status."""
        try:
            response = requests.get(
                f"{self.base_url}/files/status/{file_id}"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting status: {e}")
            return None
