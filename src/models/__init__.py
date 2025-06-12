"""
Data models for paper extraction and storage.

This module contains Pydantic models for the implemented paper metadata functionality
and text sections functionality.
"""

from .paper_metadata import PaperMetadata, generate_64bit_id
from .text_section import TextSection

__all__ = ['PaperMetadata', 'TextSection', 'generate_64bit_id']

# Future models will be added here as they are implemented:
# - Author (for detailed author information)
# - Section (for paper sections)
# - Table (for extracted tables)
# - Image (for extracted images)
# - Reference (for references)
# - Citation (for citations)
# - StatisticalData (for statistical information)
# - KeyFinding (for key findings)
