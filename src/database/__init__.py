"""
Database management module for paper extraction system.

This module provides database connection, schema management, and repository classes
for the implemented paper metadata and text sections functionality.
"""

from .connection import DatabaseConnection
from .schema_manager import SchemaManager
from .repositories import PaperMetadataRepository, TextSectionsRepository

__all__ = [
    'DatabaseConnection',
    'SchemaManager', 
    'PaperMetadataRepository',
    'TextSectionsRepository'
]
