"""
Enhanced Pydantic models for scientific paper extraction and organization.

This module defines enhanced data models for storing and organizing content extracted from
scientific papers in Markdown format, with specific focus on medical research papers.
The models are designed to preserve relationships between different components using 64-bit IDs
while capturing rich metadata and statistical information.

These enhanced models serve as the foundation for:
1. Storing comprehensive structured data in PostgreSQL
2. Building an enhanced vector database for RAG applications
3. Enabling sophisticated agent-based interactions with scientific content
4. Supporting statistical analysis and key findings extraction
"""

import re
import uuid
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from decimal import Decimal

from pydantic import BaseModel, Field, validator


def generate_64bit_id(seed: str = None) -> int:
    """
    Generate a deterministic 64-bit integer ID based on a seed string.
    
    Args:
        seed: Optional seed string to generate deterministic IDs.
            If None, a random UUID will be used.
            
    Returns:
        A 64-bit integer ID
    """
    if seed is None:
        # Generate a random UUID if no seed is provided
        seed = str(uuid.uuid4())
    
    # Create a deterministic hash based on the seed
    hash_obj = hashlib.sha256(seed.encode())
    # Get first 8 bytes (64 bits) of the hash and convert to integer
    return int.from_bytes(hash_obj.digest()[:8], byteorder='big')


def generate_hierarchical_id(paper_id: int, element_type: str, sequence: int) -> int:
    """
    Generate hierarchical IDs that maintain relationships while staying within 64-bit limit.
    
    Format: PPPPPPPP-TTTT-SSSS (conceptually, but stored as single 64-bit int)
    - P: Paper ID base (32 bits)
    - T: Element type code (16 bits)  
    - S: Sequence within type (16 bits)
    
    Args:
        paper_id: Base paper ID
        element_type: Type of element (section, table, image, etc.)
        sequence: Sequence number within the element type
        
    Returns:
        A 64-bit hierarchical ID
    """
    # Element type codes
    TYPE_CODES = {
        'section': 0x0001,
        'table': 0x0002,
        'image': 0x0003,
        'reference': 0x0004,
        'citation': 0x0005,
        'author': 0x0006,
        'statistic': 0x0007,
        'finding': 0x0008
    }
    
    # Ensure paper_id fits in 32 bits
    paper_id_32 = paper_id & 0xFFFFFFFF
    type_code = TYPE_CODES.get(element_type, 0xFFFF)
    sequence_16 = sequence & 0xFFFF
    
    # Combine into 64-bit ID
    return (paper_id_32 << 32) | (type_code << 16) | sequence_16


def generate_content_id(content: str, salt: str = "") -> int:
    """
    Generate deterministic ID based on content hash for deduplication.
    
    Args:
        content: Content to hash
        salt: Optional salt to add uniqueness
        
    Returns:
        A 64-bit content-based ID
    """
    content_with_salt = f"{content}{salt}"
    hash_obj = hashlib.sha256(content_with_salt.encode())
    return int.from_bytes(hash_obj.digest()[:8], byteorder='big')


class SectionType(str, Enum):
    """Enumeration of possible section types in a scientific paper."""
    TITLE = "title"
    ABSTRACT = "abstract"
    KEY_POINTS = "key_points"
    INTRODUCTION = "introduction"
    METHODS = "methods"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    REFERENCES = "references"
    ACKNOWLEDGMENTS = "acknowledgments"
    APPENDIX = "appendix"
    SUPPLEMENTAL = "supplemental"
    LIMITATIONS = "limitations"
    OTHER = "other"


class PaperType(str, Enum):
    """Enumeration of paper types."""
    RESEARCH_ARTICLE = "research_article"
    REVIEW = "review"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    CASE_STUDY = "case_study"
    CASE_REPORT = "case_report"
    EDITORIAL = "editorial"
    COMMENTARY = "commentary"
    OTHER = "other"


class StudyDesign(str, Enum):
    """Enumeration of study designs."""
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"
    RANDOMIZED_CONTROLLED_TRIAL = "randomized_controlled_trial"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    OBSERVATIONAL = "observational"
    EXPERIMENTAL = "experimental"
    DESCRIPTIVE = "descriptive"
    OTHER = "other"


class Author(BaseModel):
    """Model for detailed author information."""
    
    id: int = Field(..., description="64-bit unique identifier for the author")
    paper_id: int = Field(..., description="64-bit ID of the parent paper")
    name: str = Field(..., description="Full name of the author")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    email: Optional[str] = Field(None, description="Email address")
    orcid: Optional[str] = Field(None, description="ORCID identifier")
    affiliations: List[str] = Field(default_factory=list, description="List of affiliations")
    is_corresponding: bool = Field(False, description="Whether this is the corresponding author")
    sequence: int = Field(..., description="Author order in the paper")
    degrees: List[str] = Field(default_factory=list, description="Academic degrees (MD, PhD, etc.)")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    @validator('id', 'paper_id')
    def validate_id_size(cls, v):
        """Ensure the ID fits within 64 bits."""
        if v < 0 or v >= (1 << 64):
            raise ValueError("ID must be a 64-bit integer (0 to 2^64-1)")
        return v


class PaperMetadata(BaseModel):
    """
    Enhanced model for storing metadata about a scientific paper.
    
    This is the main entity that connects all components of a paper.
    """
    id: int = Field(..., description="64-bit unique identifier for the paper")
    title: str = Field(..., description="Title of the paper")
    authors: List[str] = Field(default_factory=list, description="List of author names (legacy field)")
    journal: Optional[str] = Field(None, description="Journal name")
    publication_date: Optional[str] = Field(None, description="Publication date")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    volume: Optional[str] = Field(None, description="Journal volume")
    issue: Optional[str] = Field(None, description="Journal issue")
    pages: Optional[str] = Field(None, description="Page range")
    abstract: Optional[str] = Field(None, description="Paper abstract")
    keywords: List[str] = Field(default_factory=list, description="List of keywords")
    source_file: str = Field(..., description="Source file path or name")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    # Enhanced fields for medical papers
    paper_type: PaperType = Field(PaperType.RESEARCH_ARTICLE, description="Type of paper")
    study_design: Optional[StudyDesign] = Field(None, description="Study design")
    medical_specialty: Optional[str] = Field(None, description="Medical specialty or field")
    study_population: Optional[str] = Field(None, description="Description of study population")
    study_period: Optional[str] = Field(None, description="Study period or timeframe")
    funding_sources: List[str] = Field(default_factory=list, description="Funding sources")
    conflict_of_interest: Optional[str] = Field(None, description="Conflict of interest statement")
    data_availability: Optional[str] = Field(None, description="Data availability statement")
    ethics_approval: Optional[str] = Field(None, description="Ethics approval information")
    registration_number: Optional[str] = Field(None, description="Clinical trial registration number")
    supplemental_materials: List[str] = Field(default_factory=list, description="List of supplemental materials")
    
    @validator('id')
    def validate_id_size(cls, v):
        """Ensure the ID fits within 64 bits."""
        if v < 0 or v >= (1 << 64):
            raise ValueError("ID must be a 64-bit integer (0 to 2^64-1)")
        return v


class Section(BaseModel):
    """
    Enhanced model for storing a section of text from a scientific paper.
    
    Sections are hierarchical and include enhanced metadata for medical papers.
    """
    id: int = Field(..., description="64-bit unique identifier for this section")
    paper_id: int = Field(..., description="64-bit ID of the parent paper")
    title: str = Field(..., description="Section heading")
    content: str = Field(..., description="Full text content of the section")
    section_type: SectionType = Field(SectionType.OTHER, description="Type of section")
    level: int = Field(1, description="Heading level (1 for h1, 2 for h2, etc.)")
    parent_id: Optional[int] = Field(None, description="ID of parent section, if any")
    sequence: int = Field(..., description="Sequence number to preserve document order")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    # Enhanced fields
    word_count: int = Field(0, description="Word count of the section")
    has_subsections: bool = Field(False, description="Whether this section has subsections")
    statistical_content: bool = Field(False, description="Whether section contains statistical analysis")
    methodology_description: bool = Field(False, description="Whether section describes methodology")
    contains_citations: int = Field(0, description="Number of citations in this section")
    key_findings: List[str] = Field(default_factory=list, description="Key findings mentioned in this section")


class StatisticalData(BaseModel):
    """Model for capturing statistical information from medical papers."""
    
    id: int = Field(..., description="64-bit unique identifier for this statistical data")
    paper_id: int = Field(..., description="64-bit ID of the parent paper")
    section_id: Optional[int] = Field(None, description="64-bit ID of the containing section")
    statistic_type: str = Field(..., description="Type of statistic (odds_ratio, p_value, confidence_interval, etc.)")
    value: Optional[float] = Field(None, description="Numerical value of the statistic")
    value_text: str = Field(..., description="Text representation of the statistic")
    confidence_interval: Optional[str] = Field(None, description="Confidence interval if applicable")
    p_value: Optional[float] = Field(None, description="P-value if applicable")
    context: str = Field(..., description="Context in which the statistic appears")
    variable_name: Optional[str] = Field(None, description="Variable being measured")
    comparison_groups: List[str] = Field(default_factory=list, description="Groups being compared")
    sample_size: Optional[int] = Field(None, description="Sample size for this statistic")
    sequence: int = Field(..., description="Sequence number within the paper")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")


class Table(BaseModel):
    """
    Enhanced model for storing a table from a scientific paper.
    
    Tables are linked to both the paper and their containing section with enhanced metadata.
    """
    id: int = Field(..., description="64-bit unique identifier for this table")
    paper_id: int = Field(..., description="64-bit ID of the parent paper")
    section_id: Optional[int] = Field(None, description="64-bit ID of the containing section")
    caption: Optional[str] = Field(None, description="Table caption")
    content: str = Field(..., description="Markdown or HTML representation of the table")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Structured representation of table data")
    sequence: int = Field(..., description="Sequence number to preserve document order")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    # Enhanced fields
    table_type: str = Field(default="data", description="Type of table (characteristics, results, comparison, etc.)")
    column_headers: List[str] = Field(default_factory=list, description="Column headers")
    row_count: int = Field(0, description="Number of data rows")
    column_count: int = Field(0, description="Number of columns")
    contains_statistics: bool = Field(False, description="Whether table contains statistical data")
    patient_data: bool = Field(False, description="Whether table contains patient demographic data")
    footnotes: List[str] = Field(default_factory=list, description="Table footnotes")


class Image(BaseModel):
    """
    Enhanced model for storing an image from a scientific paper.
    
    Images are linked to both the paper and their containing section with enhanced metadata.
    """
    id: int = Field(..., description="64-bit unique identifier for this image")
    paper_id: int = Field(..., description="64-bit ID of the parent paper")
    section_id: Optional[int] = Field(None, description="64-bit ID of the containing section")
    caption: Optional[str] = Field(None, description="Image caption")
    file_path: str = Field(..., description="Path to the image file")
    alt_text: Optional[str] = Field(None, description="Alternative text for the image")
    width: Optional[int] = Field(None, description="Image width in pixels")
    height: Optional[int] = Field(None, description="Image height in pixels")
    sequence: int = Field(..., description="Sequence number to preserve document order")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    # Enhanced fields
    image_type: str = Field(default="figure", description="Type of image (figure, flowchart, logo, diagram, etc.)")
    figure_number: Optional[str] = Field(None, description="Figure number (e.g., 'Figure 1', 'Figure 2A')")
    is_embedded: bool = Field(False, description="Whether image is embedded as base64")
    content_hash: Optional[str] = Field(None, description="Hash of image content for deduplication")
    contains_data_visualization: bool = Field(False, description="Whether image shows data/results")
    medical_imaging: bool = Field(False, description="Whether this is medical imaging (X-ray, MRI, etc.)")


class KeyFinding(BaseModel):
    """Model for capturing key findings and outcomes from medical papers."""
    
    id: int = Field(..., description="64-bit unique identifier for this finding")
    paper_id: int = Field(..., description="64-bit ID of the parent paper")
    section_id: Optional[int] = Field(None, description="64-bit ID of the section containing this finding")
    finding_text: str = Field(..., description="Text describing the finding")
    finding_type: str = Field(..., description="Type of finding (primary_outcome, secondary_outcome, safety, etc.)")
    statistical_significance: Optional[bool] = Field(None, description="Whether finding is statistically significant")
    clinical_significance: Optional[str] = Field(None, description="Clinical significance description")
    associated_statistics: List[int] = Field(default_factory=list, description="IDs of related statistical data")
    confidence_level: Optional[str] = Field(None, description="Confidence level of the finding")
    sequence: int = Field(..., description="Sequence number within the paper")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")


class Reference(BaseModel):
    """
    Model for storing a reference from a scientific paper.
    
    References are linked to the paper and may contain citation information.
    """
    id: int = Field(..., description="64-bit unique identifier for this reference")
    paper_id: int = Field(..., description="64-bit ID of the parent paper")
    text: str = Field(..., description="Full text of the reference")
    doi: Optional[str] = Field(None, description="DOI of the referenced paper, if available")
    sequence: int = Field(..., description="Sequence/reference number")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")


class Citation(BaseModel):
    """
    Model for storing a citation within the text of a scientific paper.
    
    Citations link to both the paper and the reference they refer to.
    """
    id: int = Field(..., description="64-bit unique identifier for this citation")
    paper_id: int = Field(..., description="64-bit ID of the parent paper")
    section_id: int = Field(..., description="64-bit ID of the section containing this citation")
    reference_id: int = Field(..., description="64-bit ID of the referenced item")
    text: str = Field(..., description="Citation text as it appears in the document")
    context: Optional[str] = Field(None, description="Surrounding text for context")
    sequence: int = Field(..., description="Sequence number to preserve document order")


class EnhancedExtractedPaper(BaseModel):
    """
    Enhanced container model that holds all components of an extracted scientific paper.
    
    This model includes all the enhanced components for comprehensive paper analysis.
    """
    metadata: PaperMetadata
    authors: List[Author] = Field(default_factory=list)
    sections: List[Section] = Field(default_factory=list)
    tables: List[Table] = Field(default_factory=list)
    images: List[Image] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    statistical_data: List[StatisticalData] = Field(default_factory=list)
    key_findings: List[KeyFinding] = Field(default_factory=list)


# Legacy support - keep original ExtractedPaper for backward compatibility
class ExtractedPaper(BaseModel):
    """
    Original container model for backward compatibility.
    """
    metadata: PaperMetadata
    sections: List[Section] = Field(default_factory=list)
    tables: List[Table] = Field(default_factory=list)
    images: List[Image] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
