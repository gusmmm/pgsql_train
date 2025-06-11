"""
File utility functions for paper processing.

This module provides file loading and handling utilities.
"""

import os
from typing import Optional
from pathlib import Path


class FileLoader:
    """
    Utility class for loading and handling paper files.
    """
    
    @staticmethod
    def load_paper_content(file_path: str) -> Optional[str]:
        """
        Load the content of a paper file.
        
        Args:
            file_path: Path to the paper file
            
        Returns:
            Paper content if successful, None otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✓ Successfully loaded paper content from: {file_path}")
            return content
        except FileNotFoundError:
            print(f"✗ Error: Paper file not found at {file_path}")
            return None
        except UnicodeDecodeError:
            print(f"✗ Error: Unable to decode file at {file_path} with UTF-8 encoding")
            return None
        except Exception as e:
            print(f"✗ Error reading paper file '{file_path}': {e}")
            return None
    
    @staticmethod
    def validate_file_exists(file_path: str) -> bool:
        """
        Validate that a file exists.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        if not FileLoader.validate_file_exists(file_path):
            return {"exists": False}
        
        path_obj = Path(file_path)
        stat = path_obj.stat()
        
        return {
            "exists": True,
            "name": path_obj.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "absolute_path": str(path_obj.absolute())
        }
