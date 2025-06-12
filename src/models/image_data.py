"""
Image data model for paper extraction system.

This module defines the ImageData model for storing and validating
image metadata and AI analysis results from scientific papers.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from .paper_metadata import generate_64bit_id


class ImageData(BaseModel):
    """
    Model for extracted images from scientific papers.
    
    This follows the project's Pydantic pattern for data validation
    and uses the established 64-bit ID system.
    """
    
    id: int = Field(..., description="64-bit unique identifier for this image")
    paper_id: Optional[int] = Field(None, description="64-bit ID of the parent paper if available")
    image_number: int = Field(..., description="Sequential order of this image in the document")
    alt_text: str = Field("", description="Alt text or caption from the markdown")
    image_data: str = Field(..., description="Base64 encoded image data")
    image_format: str = Field("", description="Image format (png, jpg, etc.) if detectable")
    summary: str = Field(..., description="AI-generated comprehensive description of the image content")
    graphic_analysis: str = Field(..., description="Detailed analysis of graphic type, elements, and structure")
    statistical_analysis: str = Field("", description="Analysis of any statistical content in the image")
    contextual_relevance: str = Field(..., description="How the image relates to the research context")
    keywords: List[str] = Field(default_factory=list, description="Keywords related to image and paper context")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    @classmethod
    def generate_image_id(cls, alt_text: str, image_data: str, image_number: int) -> int:
        """
        Generate a 64-bit ID for an image.
        
        Args:
            alt_text: Image alt text or caption
            image_data: Base64 image data (first 500 chars used for uniqueness)
            image_number: Sequential position in document
            
        Returns:
            64-bit integer ID
        """
        # Create unique input combining all image identifiers
        # Use first 500 chars of image data to ensure uniqueness while avoiding massive strings
        unique_input = f"image_{image_number}:{alt_text}:{image_data[:500]}"
        return generate_64bit_id(unique_input, f"image_{image_number}")
