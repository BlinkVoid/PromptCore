"""Safe File Manager Utility."""

import os
import re
from pathlib import Path
from typing import Optional

class SafeFileManager:
    """Utility for platform-agnostic, safe file operations."""
    
    @staticmethod
    def ensure_directory(path: Path) -> None:
        """
        Ensure a directory exists, handling permission errors gracefully.
        
        Args:
            path: The directory path to ensure.
            
        Raises:
            OSError: If directory creation fails due to permissions.
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise OSError(f"Permission denied creating directory: {path}") from e

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename to prevent path traversal and invalid characters.
        
        Args:
            filename: The raw filename string.
            
        Returns:
            A sanitized, safe filename string.
        """
        # Collapse multiple dots (prevent .. traversal)
        name = re.sub(r'\.{2,}', '.', filename)
        
        # Replace invalid chars with underscore (Windows/Unix safe)
        # Allows alphanumeric, dot, dash, underscore
        name = re.sub(r'[^\w\.\-]', '_', name)
        
        # Prevent leading dots/slashes (extra safety against hidden files/root traversal)
        name = name.lstrip('./\\')
        
        # Truncate to reasonable length (e.g., 255)
        return name[:255]

    @staticmethod
    def get_safe_path(base_dir: Path, filename: str) -> Path:
        """
        Construct a safe path within a base directory.
        
        Args:
            base_dir: The trusted root directory.
            filename: The potentially unsafe user input filename.
            
        Returns:
            A simplified, absolute path guaranteed to be inside base_dir.
            
        Raises:
            ValueError: If the resulting path attempts traversal outside base_dir.
        """
        sanitized = SafeFileManager.sanitize_filename(filename)
        safe_path = (base_dir / sanitized).resolve()
        
        # Verify it's still inside base_dir
        if not str(safe_path).startswith(str(base_dir.resolve())):
            raise ValueError(f"Path traversal detected: {filename}")
            
        return safe_path
