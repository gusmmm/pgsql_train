"""
Text Section data model for scientific papers.

This module provides the TextSection data model using Pydantic for validation
and type safety. This model represents extracted text sections from scientific papers.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# Import the existing ID generation function
from .paper_metadata import generate_64bit_id


class TextSection(BaseModel):
    """
    Model for extracted text sections from scientific papers.
    
    This follows the project's Pydantic pattern for data validation
    and uses the established 64-bit ID system.
    """
    
    id: int = Field(..., description="64-bit unique identifier for this section")
    paper_id: Optional[int] = Field(None, description="64-bit ID of the parent paper if available")
    title: str = Field(..., description="Title/heading of the section")
    content: str = Field(..., description="Full text content of the section (verbatim)")
    summary: str = Field(..., description="Comprehensive summary of the section content")
    keywords: List[str] = Field(default_factory=list, description="Key words and phrases for searching this section")
    section_number: int = Field(..., description="Sequential order of this section in the document")
    level: int = Field(1, description="Heading level (1 for main sections, 2 for subsections, etc.)")
    word_count: int = Field(0, description="Number of words in the content")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    @classmethod
    def generate_section_id(cls, title: str, content: str, section_number: int) -> int:
        """
        Generate a 64-bit ID for a text section.
        
        Args:
            title: Section title/heading
            content: Section content
            section_number: Sequential position in document
            
        Returns:
            64-bit integer ID
        """
        # Create unique input combining all section identifiers
        unique_input = f"section_{section_number}:{title}:{content[:500]}"
        return generate_64bit_id(unique_input, f"section_{section_number}")
