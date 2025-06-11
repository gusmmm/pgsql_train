"""
AI-Powered Text Section Extraction Agent for Scientific Papers.

This experimental module extracts text sections from scientific papers,
excluding references/bibliography, tables, figures, and images. 
Uses Google Generative AI for intelligent content filtering, summarization and keyword extraction.
Follows the project's OOP architecture and established AI patterns from ai_extractor.py.
"""

import os
import json
import re
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import the existing ID generation function
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from models.paper_metadata import generate_64bit_id


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


class AITextExtractionAgent:
    """
    AI-powered agent for extracting and analyzing text sections from scientific papers.
    
    This class follows the project's OOP patterns from ai_extractor.py with:
    - Single responsibility (text section extraction and AI analysis)
    - Robust error handling with boolean return values
    - Google Generative AI integration following established patterns
    - AI-driven content filtering and analysis
    """
    
    def __init__(self):
        """Initialize the AI-powered text extraction agent following ai_extractor pattern."""
        # Load environment variables
        load_dotenv()
        
        # Validate Google API key
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            raise EnvironmentError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Please set it to use the Google Generative AI API."
            )
        
        # Initialize the AI client following established pattern
        self.client = None
        self._initialize_client()
        
        print("✓ AI-powered text extraction agent initialized")
        
    def _initialize_client(self) -> None:
        """Initialize the Google Generative AI client following ai_extractor pattern."""
        try:
            self.client = genai.Client()
            print("✓ Google GenAI client initialized successfully for text analysis.")
        except Exception as e:
            print(f"✗ Error initializing Google GenAI client: {e}")
            print("Please ensure the GOOGLE_API_KEY environment variable is set and valid.")
            self.client = None
    
    def extract_text_sections(self, paper_content: str, source_file: str = "") -> List[TextSection]:
        """
        Extract text sections from paper content using AI for intelligent analysis.
        
        Args:
            paper_content: Full content of the paper
            source_file: Source file path (optional, for better ID generation)
            
        Returns:
            List of TextSection objects with AI-generated summaries and keywords
        """
        if not self.client:
            print("✗ AI client not available. Cannot proceed with intelligent extraction.")
            return []
        
        try:
            print("🔍 Starting AI-powered text section extraction...")
            
            # Use AI to extract sections with analysis in one call
            sections = self._ai_extract_and_analyze_sections(paper_content)
            
            if not sections:
                print("✗ No sections identified by AI")
                return []
            
            # Convert to TextSection objects
            text_sections = []
            for i, section_data in enumerate(sections, 1):
                title = section_data.get('title', f'Section {i}')
                content = section_data.get('content', '')
                summary = section_data.get('summary', f'Section {i} content')
                keywords = section_data.get('keywords', [])
                level = section_data.get('level', 1)
                
                if content.strip():  # Only include sections with content
                    section = TextSection(
                        id=TextSection.generate_section_id(title, content, i),
                        paper_id=None,  # Will be set when integrated with paper processing
                        title=title.strip(),
                        content=content.strip(),
                        summary=summary,
                        keywords=keywords,
                        section_number=i,
                        level=level,
                        word_count=len(content.split())
                    )
                    text_sections.append(section)
                    print(f"  ✓ Section {i}: '{title[:50]}...' analyzed with AI")
            
            print(f"✓ Successfully extracted {len(text_sections)} sections with AI analysis")
            return text_sections
            
        except Exception as e:
            print(f"✗ Error during AI-powered text section extraction: {e}")
            return []
    
    def _ai_extract_and_analyze_sections(self, paper_content: str) -> List[Dict[str, Any]]:
        """
        Use AI to intelligently extract sections with comprehensive analysis in one call.
        
        Args:
            paper_content: Full paper content
            
        Returns:
            List of section dictionaries with title, content, summary, keywords, and level
        """
        try:
            # Debug: Show first part of content being analyzed
            print(f"🔍 Paper content preview (first 300 chars): {paper_content[:300]}...")
            
            prompt = f"""You are analyzing a scientific research paper. Extract the main text sections, excluding:
- References/Bibliography
- Tables and figures 
- Image descriptions
- Acknowledgments
- Author information
- Supplemental material
- Image base64 data

For each valid text section, provide:
1. title: The section heading (e.g., "Abstract", "Introduction", "Methods", "Results", "Discussion")
2. content: The full text content (preserve original text exactly, no modifications)
3. summary: A comprehensive 2-3 sentence summary capturing main findings, methods, or key points
4. keywords: 8-15 relevant keywords including statistical methods, study types, medical terms, and key concepts
5. level: Heading level (1 for main sections, 2 for subsections, etc.)

Focus on substantial text sections containing research content, methods, results, or discussion.

Paper content to analyze:
---
{paper_content}
---

Return ONLY a valid JSON array of objects with these exact fields: 'title', 'content', 'summary', 'keywords', 'level'
Do not include any explanatory text, just the JSON array."""

            response = self.client.models.generate_content(
                model="gemini-2.5-pro-preview-06-05",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )
            
            if response.text:
                try:
                    # Debug: Show AI response preview
                    print(f"🤖 AI response preview (first 200 chars): {response.text[:200]}...")
                    
                    # Parse JSON response directly (since we specified JSON output)
                    sections_data = json.loads(response.text)
                    
                    # Validate that we got a list
                    if not isinstance(sections_data, list):
                        print("✗ AI response is not a list")
                        return []
                    
                    print(f"✓ AI extracted and analyzed {len(sections_data)} sections")
                    return sections_data
                    
                except json.JSONDecodeError as e:
                    print(f"✗ Error parsing AI response as JSON: {e}")
                    print(f"Raw response: {response.text[:500]}...")
                    return []
            else:
                print("✗ Empty response from AI for section extraction")
                return []
                
        except Exception as e:
            print(f"✗ Error during AI section extraction and analysis: {e}")
            return []
    
    def extract_and_save_json(self, paper_content: str, output_file: str, source_file: str = "") -> bool:
        """
        Extract text sections and save as JSON file using AI analysis.
        
        Args:
            paper_content: Full content of the paper
            output_file: Path to save JSON output
            source_file: Source file path (optional)
            
        Returns:
            Boolean indicating success
        """
        try:
            sections = self.extract_text_sections(paper_content, source_file)
            
            if not sections:
                print("✗ No sections extracted to save")
                return False
            
            # Convert to JSON-serializable format
            sections_data = []
            for section in sections:
                sections_data.append({
                    "id": section.id,
                    "paper_id": section.paper_id,
                    "title": section.title,
                    "content": section.content,
                    "summary": section.summary,
                    "keywords": section.keywords,
                    "section_number": section.section_number,
                    "level": section.level,
                    "word_count": section.word_count,
                    "extracted_at": section.extracted_at.isoformat()
                })
            
            # Save to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(sections_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Successfully saved {len(sections)} AI-analyzed sections to {output_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving sections to JSON: {e}")
            return False

# Example usage and testing function
def main():
    """
    Example usage of the AITextExtractionAgent.
    
    This demonstrates how to use the agent following the project's patterns.
    """
    print("🚀 Testing AI Text Extraction Agent...")
    print("=" * 60)
    
    # Initialize agent
    agent = AITextExtractionAgent()
    
    # Test with sample paper
    sample_paper_path = Path(__file__).parent.parent / "docs" / "zanella_2025-with-images.md"
    
    if sample_paper_path.exists():
        try:
            # Load paper content
            with open(sample_paper_path, 'r', encoding='utf-8') as f:
                paper_content = f.read()
            
            print(f"📄 Loaded paper: {sample_paper_path}")
            
            # Save to JSON (this will also extract and display basic info)
            output_file = Path(__file__).parent / "extracted_text_sections.json"
            success = agent.extract_and_save_json(paper_content, str(output_file), str(sample_paper_path))
            
            if success:
                print(f"\n✅ Complete! Check {output_file} for full results")
            else:
                print(f"\n✗ Failed to process paper")
            
        except Exception as e:
            print(f"✗ Error testing agent: {e}")
    else:
        print(f"✗ Sample paper not found: {sample_paper_path}")


if __name__ == "__main__":
    main()
