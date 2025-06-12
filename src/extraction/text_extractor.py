"""
AI-powered text section extraction for scientific papers.

This module provides the TextExtractor class that integrates the experimental
text agent functionality into the production pipeline.
"""

import os
import json
import re
from typing import List, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

from ..models import TextSection
from ..config.ai_models import AI_MODELS


class TextExtractor:
    """
    AI-powered extractor for scientific paper text sections.
    
    This class integrates the experimental text extraction functionality
    into the production pipeline, following the established AI patterns.
    """
    
    def __init__(self):
        """Initialize the text extractor with Google API configuration."""
        # Load environment variables
        load_dotenv()
        
        # Validate Google API key
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            raise EnvironmentError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Please set it to use the Google Generative AI API."
            )
        
        # Define model configuration once - single source of truth
        self.model_name = AI_MODELS.get_model_for_agent('text')
        self.temperature = AI_MODELS.DEFAULT_TEMPERATURE
        self.max_tokens = AI_MODELS.DEFAULT_MAX_TOKENS
        
        # Initialize the client following established pattern
        self.client = None
        self._initialize_client()
        
        # Print model configuration for transparency
        print(f"✓ Text Extractor initialized using model: {self.model_name}")
        print(f"  Temperature: {self.temperature}, Max tokens: {self.max_tokens}")
    
    def _initialize_client(self) -> None:
        """Initialize the Google Generative AI client following ai_extractor pattern."""
        try:
            self.client = genai.Client()
            print("✓ Google GenAI client initialized successfully for text extraction.")
        except Exception as e:
            print(f"✗ Error initializing Google GenAI client: {e}")
            print("Please ensure the GOOGLE_API_KEY environment variable is set and valid.")
            self.client = None
    
    def extract_text_sections(self, paper_content: str, paper_id: int) -> List[TextSection]:
        """
        Extract text sections from paper content using AI.
        
        Args:
            paper_content: Full content of the paper
            paper_id: ID of the paper to link sections to
            
        Returns:
            List of TextSection objects with AI-generated summaries and keywords
        """
        if not self.client:
            print("✗ AI client not available. Cannot proceed with text section extraction.")
            return []
        
        try:
            print("🔍 Starting AI-powered text section extraction...")
            
            # Use AI to extract sections with analysis
            sections_data = self._ai_extract_and_analyze_sections(paper_content)
            
            if not sections_data:
                print("✗ No sections identified by AI")
                return []
            
            # Convert to TextSection objects
            text_sections = []
            for i, section_data in enumerate(sections_data, 1):
                title = section_data.get('title', f'Section {i}')
                content = section_data.get('content', '')
                summary = section_data.get('summary', f'Section {i} content')
                keywords = section_data.get('keywords', [])
                level = section_data.get('level', 1)
                
                if content.strip():  # Only include sections with content
                    section = TextSection(
                        id=TextSection.generate_section_id(title, content, i),
                        paper_id=paper_id,
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
    
    def _ai_extract_and_analyze_sections(self, paper_content: str) -> List[dict]:
        """
        Use AI to intelligently extract sections with comprehensive analysis.
        
        Args:
            paper_content: Full paper content
            
        Returns:
            List of section dictionaries with title, content, summary, keywords, and level
        """
        try:
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

            print(f"  🤖 Analyzing text sections with model: {self.model_name}")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    response_mime_type="application/json",
                ),
            )
            
            if response.text:
                try:
                    # Parse JSON response directly
                    sections_data = json.loads(response.text)
                    
                    # Validate that we got a list
                    if not isinstance(sections_data, list):
                        print("✗ AI response is not a list")
                        return []
                    
                    print(f"✓ AI extracted and analyzed {len(sections_data)} sections")
                    return sections_data
                    
                except json.JSONDecodeError as e:
                    print(f"✗ Error parsing AI response as JSON: {e}")
                    return []
            else:
                print("✗ Empty response from AI for section extraction")
                return []
                
        except Exception as e:
            print(f"✗ Error during AI section extraction and analysis: {e}")
            return []
