"""
Table Data Model for Scientific Paper Processing System.

This module defines the Pydantic model for extracted tables from scientific papers,
following the project's established patterns for data validation and 64-bit ID generation.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from .paper_metadata import generate_64bit_id


class TableData(BaseModel):
    """
    Pydantic model for extracted tables from scientific papers.
    
    This model represents structured data extracted from markdown tables,
    including AI-generated analysis, summaries, and contextual information.
    
    Attributes:
        id: 64-bit unique identifier for this table
        paper_id: 64-bit ID of the parent paper (foreign key)
        table_number: Sequential order of this table in the document
        title: AI-generated descriptive title/caption of the table
        raw_content: Raw markdown table content (verbatim)
        summary: AI-generated comprehensive summary of table contents
        context_analysis: AI analysis of table's role in the research context
        statistical_findings: AI-identified statistical results and conclusions
        keywords: AI-generated keywords for searchability
        column_count: Number of columns in the table
        row_count: Number of data rows (excluding header)
        extracted_at: Timestamp when extraction was performed
    """
    
    id: int = Field(
        ..., 
        description="64-bit unique identifier for this table"
    )
    paper_id: Optional[int] = Field(
        None, 
        description="64-bit ID of the parent paper (foreign key reference)"
    )
    table_number: int = Field(
        ..., 
        description="Sequential order of this table in the document (1, 2, 3, ...)"
    )
    title: str = Field(
        ..., 
        description="AI-generated descriptive title/caption of the table"
    )
    raw_content: str = Field(
        ..., 
        description="Raw markdown table content preserved verbatim"
    )
    summary: str = Field(
        ..., 
        description="AI-generated comprehensive summary of what the table shows"
    )
    context_analysis: str = Field(
        ..., 
        description="AI analysis of the table's significance in research context"
    )
    statistical_findings: str = Field(
        ..., 
        description="AI-identified statistical results, conclusions, and key findings"
    )
    keywords: List[str] = Field(
        default_factory=list, 
        description="AI-generated keywords for search and categorization"
    )
    column_count: int = Field(
        0, 
        description="Number of columns in the table structure"
    )
    row_count: int = Field(
        0, 
        description="Number of data rows (excluding header and separator rows)"
    )
    extracted_at: datetime = Field(
        default_factory=datetime.now, 
        description="Timestamp when the table extraction was performed"
    )
    
    @classmethod
    def generate_table_id(cls, title: str, content: str, table_number: int) -> int:
        """
        Generate a unique 64-bit ID for a table using established ID generation patterns.
        
        This method follows the project's standard approach for creating unique identifiers
        that are deterministic based on content but globally unique.
        
        Args:
            title: Table title/caption
            content: Table content (first 500 chars used for uniqueness)
            table_number: Sequential position in document
            
        Returns:
            64-bit integer ID that uniquely identifies this table
            
        Example:
            >>> table_id = TableData.generate_table_id(
            ...     "Patient Demographics", 
            ...     "| Age | Count |\n|-----|-------|\n| 25-34 | 150 |", 
            ...     1
            ... )
            >>> isinstance(table_id, int)
            True
        """
        # Create unique input combining all table identifiers
        # Use first 500 chars of content to ensure uniqueness while avoiding massive strings
        unique_input = f"table_{table_number}:{title}:{content[:500]}"
        return generate_64bit_id(unique_input, f"table_{table_number}")

    class Config:
        """Pydantic model configuration."""
        # Allow extra validation and serialization features
        validate_assignment = True
        # Ensure datetime objects are serialized properly
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
