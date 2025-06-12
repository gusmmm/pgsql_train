"""
AI-Powered References/Bibliography Extraction Agent for Scientific Papers.

This experimental module extracts references from scientific papers in markdown format,
using Google Generative AI for intelligent reference parsing and analysis.
Follows the project's OOP architecture and established AI patterns from text_extractor.py.
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

# Import the existing ID generation function and AI model configuration
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from models.paper_metadata import generate_64bit_id
from config.ai_models import AI_MODELS


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


class AIReferencesExtractionAgent:
    """
    AI-powered agent for extracting references/bibliography from scientific papers.
    
    This class follows the project's OOP patterns from text_extractor.py with:
    - Single responsibility (references extraction)
    - Robust error handling with boolean return values
    - Google Generative AI integration following established patterns
    - AI-driven reference parsing and analysis
    """
    
    def __init__(self):
        """Initialize the AI-powered references extraction agent following established patterns."""
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
        
        # Initialize the AI client following established pattern
        self.client = None
        self._initialize_client()
        
        # Print model configuration for transparency
        print(f"✓ AI-powered references extraction agent initialized using model: {self.model_name}")
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
    
    def extract_references(self, paper_content: str, paper_id: Optional[int] = None) -> Optional[ReferencesData]:
        """
        Extract references/bibliography from paper content using AI.
        
        Args:
            paper_content: Full markdown content of the paper
            paper_id: Optional paper ID to link references to their parent paper
            
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
                id=ReferencesData.generate_references_id(paper_id or 0, len(references_list)),
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
                    print(f"Response text: {response.text[:500]}...")
                    return []
            else:
                print("✗ Empty response from AI for references extraction")
                return []
                
        except Exception as e:
            print(f"✗ Error during AI references extraction: {e}")
            return []
    
    def extract_and_save_json(self, paper_content: str, output_file: str, source_file: str = "", paper_id: Optional[int] = None) -> bool:
        """
        Extract references and save as JSON file using AI analysis.
        
        Args:
            paper_content: Full content of the paper
            output_file: Path to save JSON output
            source_file: Source file path (optional)
            paper_id: Paper ID to link references to
            
        Returns:
            Boolean indicating success
        """
        try:
            references_data = self.extract_references(paper_content, paper_id)
            
            if not references_data:
                print("✗ No references extracted to save")
                return False
            
            # Convert to JSON-serializable format
            output_data = {
                "id": references_data.id,
                "paper_id": references_data.paper_id,
                "reference_count": references_data.reference_count,
                "references": references_data.references,
                "extracted_at": references_data.extracted_at.isoformat(),
                "source_file": source_file
            }
            
            # Save to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Successfully saved {references_data.reference_count} references to {output_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving references to JSON: {e}")
            return False


# Example usage and testing function
def main():
    """
    Example usage of the AIReferencesExtractionAgent.
    
    This demonstrates how to use the agent following the project's patterns.
    """
    print("🚀 Testing AI References Extraction Agent...")
    print("=" * 60)
    
    # Initialize agent
    agent = AIReferencesExtractionAgent()
    
    # Test with sample paper
    sample_paper_path = Path(__file__).parent.parent / "docs" / "zanella_2025-with-images.md"
    
    if sample_paper_path.exists():
        try:
            # Load paper content
            with open(sample_paper_path, 'r', encoding='utf-8') as f:
                paper_content = f.read()
            
            print(f"📄 Loaded paper: {sample_paper_path}")
            
            # Generate a sample paper ID for testing
            sample_paper_id = 12345
            
            # Extract and save references
            output_file = Path(__file__).parent / "extracted_references.json"
            success = agent.extract_and_save_json(
                paper_content, 
                str(output_file), 
                str(sample_paper_path),
                sample_paper_id
            )
            
            if success:
                print(f"\n✅ Complete! Check {output_file} for full results")
                
                # Display summary
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    print(f"\n📊 Summary:")
                    print(f"   References ID: {data['id']}")
                    print(f"   Paper ID: {data['paper_id']}")
                    print(f"   Total references: {data['reference_count']}")
                    print(f"   First 3 references:")
                    for i, ref in enumerate(data['references'][:3], 1):
                        print(f"     {i}. {ref[:100]}...")
                        
                except Exception as e:
                    print(f"⚠️  Could not display summary: {e}")
            else:
                print(f"\n✗ Failed to process paper")
            
        except Exception as e:
            print(f"✗ Error testing agent: {e}")
    else:
        print(f"✗ Sample paper not found: {sample_paper_path}")


if __name__ == "__main__":
    main()
