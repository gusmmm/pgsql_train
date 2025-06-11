"""
Data models for paper extraction and storage.

This module contains Pydantic models for the implemented paper metadata functionality.
Additional models for sections, tables, images, etc. will be added as they are implemented.
"""

from .paper_metadata import PaperMetadata, generate_64bit_id

__all__ = ['PaperMetadata', 'generate_64bit_id']

# Future models will be added here as they are implemented:
# - Author (for detailed author information)
# - Section (for paper sections)
# - Table (for extracted tables)
# - Image (for extracted images)
# - Reference (for references)
# - Citation (for citations)
# - StatisticalData (for statistical information)
# - KeyFinding (for key findings)
