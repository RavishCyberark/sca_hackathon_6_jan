"""File handling utilities."""

import os
from pathlib import Path
from typing import Optional


class FileHandler:
    """Utility class for file operations."""
    
    def __init__(self, base_path: str = "."):
        """Initialize FileHandler with a base path.
        
        Args:
            base_path: Base directory for file operations
        """
        self.base_path = Path(base_path).resolve()
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Read contents of a file.
        
        Args:
            file_path: Path to the file (relative to base_path or absolute)
            
        Returns:
            File contents or None if file doesn't exist
        """
        path = self._resolve_path(file_path)
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error reading file {path}: {e}")
            return None
    
    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to a file.
        
        Args:
            file_path: Path to the file (relative to base_path or absolute)
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        path = self._resolve_path(file_path)
        
        try:
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file {path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists
        """
        path = self._resolve_path(file_path)
        return path.exists() and path.is_file()
    
    def ensure_directory(self, dir_path: str) -> bool:
        """Ensure a directory exists, creating it if necessary.
        
        Args:
            dir_path: Directory path to ensure
            
        Returns:
            True if directory exists or was created
        """
        path = self._resolve_path(dir_path)
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False
    
    def list_files(
        self,
        dir_path: str = ".",
        pattern: str = "*",
        recursive: bool = False
    ) -> list[str]:
        """List files in a directory.
        
        Args:
            dir_path: Directory to list
            pattern: Glob pattern for filtering
            recursive: Whether to search recursively
            
        Returns:
            List of file paths relative to base_path
        """
        path = self._resolve_path(dir_path)
        
        try:
            if recursive:
                files = list(path.rglob(pattern))
            else:
                files = list(path.glob(pattern))
            
            return [str(f.relative_to(self.base_path)) for f in files if f.is_file()]
        except Exception:
            return []
    
    def get_relative_path(self, file_path: str) -> str:
        """Get path relative to base_path.
        
        Args:
            file_path: Absolute or relative path
            
        Returns:
            Path relative to base_path
        """
        path = self._resolve_path(file_path)
        try:
            return str(path.relative_to(self.base_path))
        except ValueError:
            return str(path)
    
    def _resolve_path(self, file_path: str) -> Path:
        """Resolve a path relative to base_path or as absolute.
        
        Args:
            file_path: Path to resolve
            
        Returns:
            Resolved Path object
        """
        path = Path(file_path)
        if path.is_absolute():
            return path
        return self.base_path / path


def save_generated_test(
    output_dir: str,
    filename: str,
    content: str
) -> str:
    """Save a generated test file.
    
    Args:
        output_dir: Directory to save the file in
        filename: Name of the file
        content: Test code content
        
    Returns:
        Full path to the saved file
    """
    handler = FileHandler()
    
    # Ensure the output directory exists
    handler.ensure_directory(output_dir)
    
    # Build the full path
    file_path = os.path.join(output_dir, filename)
    
    # Write the file
    handler.write_file(file_path, content)
    
    return file_path

