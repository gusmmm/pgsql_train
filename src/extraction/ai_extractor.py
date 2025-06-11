"""
AI-powered paper extraction using Google Generative AI.

This module provides the AIExtractor class that uses Google's Generative AI
to extract structured metadata from scientific papers.
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

from ..models import PaperMetadata


class AIExtractor:
    """
    AI-powered extractor for scientific paper metadata.
    
    This class uses Google Generative AI to extract structured metadata
    from scientific paper content.
    """
    
    def __init__(self):
        """Initialize the AI extractor with Google API configuration."""
        # Load environment variables
        load_dotenv()
        
        # Validate Google API key
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            raise EnvironmentError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Please set it to use the Google Generative AI API."
            )
        
        # Initialize the client
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Google Generative AI client."""
        try:
            self.client = genai.Client()
            print("✓ Google GenAI client initialized successfully.")
        except Exception as e:
            print(f"✗ Error initializing Google GenAI client: {e}")
            print("Please ensure the GOOGLE_API_KEY environment variable is set and valid.")
            self.client = None
    
    def extract_metadata(self, paper_content: str, source_file: str) -> Optional[PaperMetadata]:
        """
        Extract metadata from paper content using Google Generative AI.
        
        Args:
            paper_content: The content of the paper
            source_file: Path to the source file
            
        Returns:
            PaperMetadata instance if successful, None if failed
        """
        if not self.client:
            print("✗ Google GenAI client not initialized. Cannot proceed with extraction.")
            return None
        
        try:
            # Generate 64-bit ID for this paper
            paper_id = PaperMetadata.generate_id(paper_content, source_file)
            print(f"✓ Generated 64-bit ID: {paper_id}")
            
            # Construct the prompt
            prompt = self._build_extraction_prompt(paper_id, source_file, paper_content)
            
            print("✓ Sending request to Google Generative AI...")
            response = self.client.models.generate_content(
                model="gemini-2.5-pro-preview-06-05",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PaperMetadata,
                    temperature=0.1,
                ),
            )
            
            print("✓ Received response from Google Generative AI.")
            
            # Parse the response
            if response.text:
                try:
                    metadata_dict = json.loads(response.text)
                    print("✓ Successfully extracted and parsed metadata.")
                    
                    # Create PaperMetadata instance
                    paper_metadata = PaperMetadata(**metadata_dict)
                    return paper_metadata
                    
                except json.JSONDecodeError as e:
                    print(f"✗ Error decoding JSON from AI response: {e}")
                    print("Raw response text was:")
                    print(response.text)
                    return None
                except Exception as e:
                    print(f"✗ Error creating PaperMetadata instance: {e}")
                    print("Raw response text was:")
                    print(response.text)
                    return None
            else:
                print("✗ AI response was empty.")
                return None
                
        except Exception as e:
            print(f"✗ Error during metadata extraction: {e}")
            return None
    
    def _build_extraction_prompt(self, paper_id: int, source_file: str, paper_content: str) -> str:
        """
        Build the extraction prompt for the AI model.
        
        Args:
            paper_id: Generated paper ID
            source_file: Source file path
            paper_content: Paper content
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Please extract metadata from the following medical research paper.
The output must be a JSON object that strictly conforms to the PaperMetadata schema provided to you.
Do not change the schema or add any additional fields.
Do not change the content of the fields or the Paper Content, just extract the information as accurately as possible.

Key instructions for specific fields:
- 'id': Use this exact value: {paper_id}
- 'source_file': This field must be exactly: "{source_file}"
- 'extracted_at': This field should represent the current timestamp when you process this (e.g., {datetime.now().isoformat()}).
- For other fields, extract them from the paper content. If a field is not present, omit it if it's Optional, or use an appropriate default if specified in the schema.

Paper Content:
---
{paper_content}
---
"""
        return prompt
    
    def extract_and_display(self, paper_content: str, source_file: str) -> Optional[PaperMetadata]:
        """
        Extract metadata and display the results in a formatted way.
        
        Args:
            paper_content: The content of the paper
            source_file: Path to the source file
            
        Returns:
            PaperMetadata instance if successful, None if failed
        """
        print("🤖 Starting AI-powered metadata extraction...")
        
        # Extract metadata
        paper_metadata = self.extract_metadata(paper_content, source_file)
        
        if paper_metadata:
            # Display extracted metadata
            print("\n📄 Extracted Metadata:")
            print("=" * 60)
            print(f"ID: {paper_metadata.id}")
            print(f"Title: {paper_metadata.title}")
            print(f"Authors: {', '.join(paper_metadata.authors) if paper_metadata.authors else 'N/A'}")
            print(f"Journal: {paper_metadata.journal or 'N/A'}")
            print(f"Publication Date: {paper_metadata.publication_date or 'N/A'}")
            print(f"DOI: {paper_metadata.doi or 'N/A'}")
            print(f"Keywords: {', '.join(paper_metadata.keywords) if paper_metadata.keywords else 'N/A'}")
            print(f"Source File: {paper_metadata.source_file}")
            print("=" * 60)
            
            if paper_metadata.abstract:
                print(f"\nAbstract:\n{paper_metadata.abstract[:200]}{'...' if len(paper_metadata.abstract) > 200 else ''}")
            
        return paper_metadata
