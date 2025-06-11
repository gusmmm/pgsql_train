"""
Core data models for paper extraction system.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import hashlib


def generate_64bit_id(content: str, source_file: str) -> int:
    """
    Generate a 64-bit ID based on paper content and source file.
    
    Args:
        content: Paper content string
        source_file: Source file path
        
    Returns:
        64-bit integer ID
    """
    # Combine content and source file for uniqueness
    combined_input = f"{source_file}:{content[:1000]}"  # Use first 1000 chars
    
    # Create SHA-256 hash
    hash_object = hashlib.sha256(combined_input.encode('utf-8'))
    hash_hex = hash_object.hexdigest()
    
    # Convert first 16 hex characters to integer (64 bits)
    hash_64bit = int(hash_hex[:16], 16)
    
    # Ensure it's a positive 64-bit integer
    return hash_64bit & 0x7FFFFFFFFFFFFFFF


class PaperMetadata(BaseModel):
    """
    Pydantic model for scientific paper metadata.
    
    This model represents the core paper information that is currently
    implemented and stored in the papers.paper_metadata table.
    """
    
    # Core identification and bibliographic information
    id: int = Field(..., description="64-bit unique identifier for the paper")
    title: str = Field(..., description="Title of the paper")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    journal: Optional[str] = Field(None, description="Journal name")
    publication_date: Optional[str] = Field(None, description="Publication date")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    volume: Optional[str] = Field(None, description="Journal volume")
    issue: Optional[str] = Field(None, description="Journal issue")
    pages: Optional[str] = Field(None, description="Page range")
    abstract: Optional[str] = Field(None, description="Paper abstract")
    keywords: List[str] = Field(default_factory=list, description="List of keywords")
    
    # Source and extraction information
    source_file: str = Field(..., description="Source file path or name")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    # Funding and ethical considerations
    funding_sources: List[str] = Field(default_factory=list, description="Funding sources")
    conflict_of_interest: Optional[str] = Field(None, description="Conflict of interest statement")
    data_availability: Optional[str] = Field(None, description="Data availability statement")
    ethics_approval: Optional[str] = Field(None, description="Ethics approval information")
    registration_number: Optional[str] = Field(None, description="Clinical trial registration number")
    
    # Supplemental materials
    supplemental_materials: List[str] = Field(default_factory=list, description="List of supplemental materials")

    @validator('id')
    def validate_id_size(cls, v):
        """Ensure the ID fits within 64 bits."""
        if v < 0 or v >= (1 << 64):
            raise ValueError("ID must be a 64-bit integer (0 to 2^64-1)")
        return v

    @classmethod
    def generate_id(cls, content: str, source_file: str) -> int:
        """
        Generate a 64-bit ID for the paper.
        
        Args:
            content: Paper content
            source_file: Source file path
            
        Returns:
            64-bit integer ID
        """
        return generate_64bit_id(content, source_file)
