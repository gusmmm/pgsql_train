"""
Data models for paper extraction and storage.

This module contains Pydantic models for the implemented paper metadata functionality,
text sections functionality, table extraction functionality, image extraction functionality,
and references extraction functionality.
"""

from .paper_metadata import PaperMetadata, generate_64bit_id
from .text_section import TextSection
from .table_data import TableData
from .image_data import ImageData
from .references_data import ReferencesData

__all__ = ['PaperMetadata', 'TextSection', 'TableData', 'ImageData', 'ReferencesData', 'generate_64bit_id']

# Future models will be added here as they are implemented:
# - Author (for detailed author information)
# - Section (for paper sections)
# - Citation (for citations)
# - StatisticalData (for statistical information)
# - KeyFinding (for key findings)
