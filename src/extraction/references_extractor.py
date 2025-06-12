"""
AI-powered references extraction for scientific papers.

This module provides the ReferencesExtractor class that integrates the experimental
references extraction functionality into the production pipeline.
"""

import os
import json
from typing import List, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

from ..models import ReferencesData
from ..config.ai_models import AI_MODELS


class ReferencesExtractor:
    """
    AI-powered extractor for scientific paper references/bibliography.
    
    This class integrates the experimental references extraction functionality
    into the production pipeline, following the established AI patterns.
    """
    
    def __init__(self):
        """Initialize the references extractor with Google API configuration."""
        # Load environment variables
        load_dotenv()
        
        # Check for API keys following established pattern
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if self.google_api_key and self.gemini_api_key:
            print("Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.")
        
        if not self.google_api_key and not self.gemini_api_key:
            raise EnvironmentError(
                "Neither GOOGLE_API_KEY nor GEMINI_API_KEY environment variable is set. "
                "Please set one of them to use the Google Generative AI API."
            )
        
        # Define model configuration once - single source of truth
        self.model_name = AI_MODELS.get_model_for_agent('text')  # Use text model for references
        self.temperature = AI_MODELS.DEFAULT_TEMPERATURE
        self.max_tokens = AI_MODELS.DEFAULT_MAX_TOKENS
        
        # Initialize the client following established pattern
        self.client = None
        self._initialize_client()
        
        # Print model configuration for transparency
        print(f"✓ References Extractor initialized using model: {self.model_name}")
        print(f"  Temperature: {self.temperature}, Max tokens: {self.max_tokens}")
    
    def _initialize_client(self) -> None:
        """Initialize the Google Generative AI client following established patterns."""
        try:
            self.client = genai.Client()
            print("✓ Google GenAI client initialized successfully for references extraction.")
        except Exception as e:
            print(f"✗ Error initializing Google GenAI client: {e}")
            print("Please ensure the API key environment variable is set and valid.")
            self.client = None
    
    def extract_references(self, paper_content: str, paper_id: int) -> Optional[ReferencesData]:
        """
        Extract references/bibliography from paper content using AI.
        
        Args:
            paper_content: Full content of the paper
            paper_id: ID of the paper to link references to
            
        Returns:
            ReferencesData object with extracted references or None if extraction failed
        """
        if not self.client:
            print("✗ AI client not available. Cannot proceed with references extraction.")
            return None
        
        try:
            print("🔍 Starting AI-powered references extraction...")
            
            # Use AI to extract references
            references_list = self._ai_extract_references(paper_content)
            
            if not references_list:
                print("✗ No references found in paper content")
                return None
            
            print(f"📚 Found {len(references_list)} references")
            
            # Create ReferencesData object
            references_data = ReferencesData(
                id=ReferencesData.generate_references_id(paper_id, len(references_list)),
                paper_id=paper_id,
                references=references_list,
                reference_count=len(references_list)
            )
            
            print(f"✓ Successfully extracted {len(references_list)} references")
            return references_data
            
        except Exception as e:
            print(f"✗ Error during references extraction: {e}")
            return None
    
    def _ai_extract_references(self, paper_content: str) -> List[str]:
        """
        Use AI to intelligently extract references from paper content.
        
        Args:
            paper_content: Full paper content
            
        Returns:
            List of reference strings as they appear in the original text
        """
        try:
            # Construct prompt following best practices for reference extraction
            prompt = f"""You are analyzing a scientific research paper to extract all references from the References, Bibliography, or Works Cited section.

Your task:
1. Identify the References/Bibliography section in the paper
2. Extract each reference exactly as it appears in the original text
3. Preserve the original formatting, punctuation, and capitalization
4. Include ALL references found, regardless of format or style
5. Do not modify, correct, or reformat the references
6. Exclude any text that is not a reference (like section headers)

Paper content to analyze:
---
{paper_content}
---

Return ONLY a valid JSON array of strings, where each string is one complete reference exactly as it appears in the original text.
Example format: ["Reference 1 text here", "Reference 2 text here", ...]
Do not include any explanatory text, just the JSON array of reference strings."""

            print(f"  🤖 Analyzing references with model: {self.model_name}")
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
                    # Parse JSON response
                    references_list = json.loads(response.text)
                    
                    # Validate that we got a list of strings
                    if not isinstance(references_list, list):
                        print("✗ AI response is not a list")
                        return []
                    
                    # Filter out empty or very short references
                    valid_references = []
                    for ref in references_list:
                        if isinstance(ref, str) and len(ref.strip()) > 10:  # Minimum length filter
                            valid_references.append(ref.strip())
                        else:
                            print(f"⚠️  Skipping invalid reference: {ref}")
                    
                    print(f"✓ AI extracted {len(valid_references)} valid references")
                    return valid_references
                    
                except json.JSONDecodeError as e:
                    print(f"✗ Error parsing AI response as JSON: {e}")
                    return []
            else:
                print("✗ Empty response from AI for references extraction")
                return []
                
        except Exception as e:
            print(f"✗ Error during AI references extraction: {e}")
            return []
