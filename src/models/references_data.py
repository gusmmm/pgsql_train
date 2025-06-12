"""
References data model for paper extraction system.

This module defines the ReferencesData model for storing and validating
references/bibliography data from scientific papers.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from .paper_metadata import generate_64bit_id


class ReferencesData(BaseModel):
    """
    Model for extracted references from scientific papers.
    
    This follows the project's Pydantic pattern for data validation
    and uses the established 64-bit ID system.
    """
    
    id: int = Field(..., description="64-bit unique identifier for this references list")
    paper_id: Optional[int] = Field(None, description="64-bit ID of the parent paper if available")
    references: List[str] = Field(default_factory=list, description="List of references as they appear in original text")
    reference_count: int = Field(..., description="Total number of references found")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    @classmethod
    def generate_references_id(cls, paper_id: int, reference_count: int) -> int:
        """
        Generate a 64-bit ID for a references list.
        
        Args:
            paper_id: ID of the parent paper
            reference_count: Number of references found
            
        Returns:
            64-bit integer ID
        """
        # Create unique input combining paper ID and reference count
        unique_input = f"references_{paper_id}:{reference_count}"
        return generate_64bit_id(unique_input, f"references_{paper_id}")
