"""
File storage service.

Manages temporary file storage for correction pipeline.
"""

from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import tempfile
import shutil
import uuid


class FileStorageService:
    """Service for managing file storage."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize file storage service."""
        if base_dir is None:
            base_dir = Path(tempfile.gettempdir()) / "text_correction"
        
        self.base_dir = base_dir
        self.storage: Dict[str, Dict[str, str]] = {}
    
    def create_file_entry(self, filename: str) -> str:
        """Create a new file entry and return file_id."""
        file_id = str(uuid.uuid4())
        
        # Create directory for this file
        file_dir = self.base_dir / file_id
        file_dir.mkdir(parents=True, exist_ok=True)
        
        # Define file paths
        original_path = file_dir / "original.txt"
        intermediate_path = file_dir / "intermediate.txt"
        final_path = file_dir / "final.txt"
        
        # Store metadata
        self.storage[file_id] = {
            "original_filename": filename,
            "original_path": str(original_path),
            "intermediate_path": str(intermediate_path),
            "final_path": str(final_path),
            "timestamp": datetime.now().isoformat(),
            "t5_applied": False
        }
        
        return file_id
    
    def save_file(self, file_id: str, file_type: str, content: str):
        """Save file content."""
        if file_id not in self.storage:
            raise ValueError(f"File ID {file_id} not found")
        
        file_path = Path(self.storage[file_id][f"{file_type}_path"])
        file_path.write_text(content, encoding='utf-8')
    
    def get_file_path(self, file_id: str, file_type: str) -> Path:
        """Get file path for a given file_id and type."""
        if file_id not in self.storage:
            raise ValueError(f"File ID {file_id} not found")
        
        return Path(self.storage[file_id][f"{file_type}_path"])
    
    def get_metadata(self, file_id: str) -> dict:
        """Get metadata for a file."""
        if file_id not in self.storage:
            raise ValueError(f"File ID {file_id} not found")
        
        return self.storage[file_id]
    
    def update_metadata(self, file_id: str, **kwargs):
        """Update metadata for a file."""
        if file_id not in self.storage:
            raise ValueError(f"File ID {file_id} not found")
        
        self.storage[file_id].update(kwargs)
    
    def file_exists(self, file_id: str) -> bool:
        """Check if file exists in storage."""
        return file_id in self.storage
    
    def cleanup_file(self, file_id: str):
        """Clean up files for a given file_id."""
        if file_id not in self.storage:
            raise ValueError(f"File ID {file_id} not found")
        
        # Remove directory
        file_dir = Path(self.storage[file_id]["original_path"]).parent
        if file_dir.exists():
            shutil.rmtree(file_dir)
        
        # Remove from storage
        del self.storage[file_id]
