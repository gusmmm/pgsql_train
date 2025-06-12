"""
AI-Powered Image Extraction Agent for Scientific Papers.

This experimental module extracts images from scientific papers in markdown format,
including base64-encoded images. Uses Google Generative AI for intelligent image analysis,
description generation, and keyword extraction.
Follows the project's OOP architecture and established AI patterns from ai_extractor.py and text_agent.py.
"""

import os
import json
import re
import base64
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


class ImageData(BaseModel):
    """
    Model for extracted images from scientific papers.
    
    This follows the project's Pydantic pattern for data validation
    and uses the established 64-bit ID system.
    """
    
    id: int = Field(..., description="64-bit unique identifier for this image")
    paper_id: Optional[int] = Field(None, description="64-bit ID of the parent paper if available")
    image_number: int = Field(..., description="Sequential order of this image in the document")
    title: str = Field(..., description="Title/caption of the image or AI-generated title")
    image_type: str = Field(..., description="Type of image (chart, graph, diagram, photo, etc.)")
    format: str = Field(..., description="Image format (png, jpg, etc.)")
    base64_data: str = Field(..., description="Base64-encoded image data")
    description: str = Field(..., description="Detailed AI-generated description of the image content")
    statistical_analysis: str = Field(..., description="Statistical analysis present in the image if any")
    keywords: List[str] = Field(default_factory=list, description="Keywords related to the image and paper context")
    width: Optional[int] = Field(None, description="Image width in pixels if available")
    height: Optional[int] = Field(None, description="Image height in pixels if available")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    @classmethod
    def generate_image_id(cls, image_data: str, image_number: int) -> int:
        """
        Generate a 64-bit ID for an image.
        
        Args:
            image_data: Base64 image data (first 500 chars used for uniqueness)
            image_number: Sequential position in document
            
        Returns:
            64-bit integer ID
        """
        # Create unique input combining image number and data sample
        unique_input = f"image_{image_number}:{image_data[:500]}"
        return generate_64bit_id(unique_input, f"image_{image_number}")


class AIImageExtractionAgent:
    """
    AI-powered agent for extracting and analyzing images from scientific papers.
    
    This class follows the project's OOP patterns from ai_extractor.py and text_agent.py with:
    - Single responsibility (image extraction and AI analysis)
    - Robust error handling with boolean return values
    - Google Generative AI integration following established patterns
    - AI-driven image content analysis and interpretation
    """
    
    def __init__(self):
        """Initialize the AI-powered image extraction agent following established patterns."""
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
        
        # Initialize the AI client
        self.client = None
        self._initialize_client()
        
        print("✓ AI-powered image extraction agent initialized")
        
    def _initialize_client(self) -> None:
        """Initialize the Google Generative AI client following established patterns."""
        try:
            self.client = genai.Client()
            print("✓ Google GenAI client initialized successfully for image analysis.")
        except Exception as e:
            print(f"✗ Error initializing Google GenAI client: {e}")
            print("Please ensure the API key environment variable is set and valid.")
            self.client = None
    
    def extract_images(self, paper_content: str, paper_id: Optional[int] = None) -> List[ImageData]:
        """
        Extract and analyze images from paper content using AI.
        
        Args:
            paper_content: Full markdown content of the paper
            paper_id: Optional paper ID to link images to their parent paper
            
        Returns:
            List of ImageData objects with comprehensive AI analysis
        """
        if not self.client:
            print("✗ AI client not available. Cannot proceed with image extraction.")
            return []
        
        try:
            print("🔍 Starting AI-powered image extraction...")
            
            # Extract base64 images from markdown
            base64_images = self._extract_base64_images_from_markdown(paper_content)
            
            if not base64_images:
                print("✗ No base64 images found in markdown content")
                return []
            
            print(f"🖼️ Found {len(base64_images)} base64 images, analyzing with AI...")
            
            # Process each image with AI
            image_data_list = []
            for i, image_info in enumerate(base64_images, 1):
                try:
                    # Get AI analysis for this image
                    analysis = self._ai_analyze_image(image_info, paper_content, i)
                    
                    if analysis:
                        # Create ImageData object
                        image_data = ImageData(
                            id=ImageData.generate_image_id(image_info['data'], i),
                            paper_id=paper_id,
                            image_number=i,
                            title=analysis.get('title', f'Figure {i}'),
                            image_type=analysis.get('image_type', 'unknown'),
                            format=image_info['format'],
                            base64_data=image_info['data'],
                            description=analysis.get('description', ''),
                            statistical_analysis=analysis.get('statistical_analysis', ''),
                            keywords=analysis.get('keywords', [])
                        )
                        image_data_list.append(image_data)
                        print(f"  ✓ Image {i}: '{image_data.title[:50]}...' analyzed with AI")
                    else:
                        print(f"  ✗ Image {i}: AI analysis failed")
                        
                except Exception as e:
                    print(f"  ✗ Image {i}: Error during analysis: {e}")
                    continue
            
            print(f"✓ Successfully extracted and analyzed {len(image_data_list)} images")
            return image_data_list
            
        except Exception as e:
            print(f"✗ Error during image extraction: {e}")
            return []
    
    def _extract_base64_images_from_markdown(self, content: str) -> List[Dict[str, str]]:
        """
        Extract base64 image data from markdown content.
        
        Args:
            content: Full markdown content
            
        Returns:
            List of dictionaries with 'format' and 'data' keys
        """
        try:
            # Regex pattern to match base64 images in markdown
            # Matches: ![alt text](data:image/format;base64,data)
            image_pattern = r'!\[([^\]]*)\]\(data:image/([^;]+);base64,([^)]+)\)'
            
            matches = re.findall(image_pattern, content)
            
            images = []
            for alt_text, image_format, base64_data in matches:
                # Clean up base64 data (remove any whitespace/newlines)
                clean_data = re.sub(r'\s+', '', base64_data)
                
                # Validate base64 data
                if self._is_valid_base64(clean_data):
                    images.append({
                        'alt_text': alt_text,
                        'format': image_format.lower(),
                        'data': clean_data
                    })
                else:
                    print(f"⚠️ Warning: Invalid base64 data found for image with alt text: '{alt_text}'")
            
            return images
            
        except Exception as e:
            print(f"✗ Error extracting base64 images: {e}")
            return []
    
    def _is_valid_base64(self, data: str) -> bool:
        """
        Validate if a string is valid base64 data.
        
        Args:
            data: String to validate
            
        Returns:
            True if valid base64, False otherwise
        """
        try:
            # Try to decode the base64 data
            base64.b64decode(data, validate=True)
            return True
        except Exception:
            return False
    
    def _ai_analyze_image(self, image_info: Dict[str, str], paper_context: str, image_number: int) -> Optional[Dict[str, Any]]:
        """
        Use AI to analyze an image in the context of the research paper.
        
        Args:
            image_info: Dictionary containing image data and metadata
            paper_context: Full paper content for context
            image_number: Sequential number of this image
            
        Returns:
            Dictionary with analysis results or None if analysis failed
        """
        try:
            if not self.client:
                print(f"✗ AI client not available for image {image_number} analysis")
                return None
            
            # Truncate paper context to avoid token limits
            context_preview = paper_context[:3000] + "..." if len(paper_context) > 3000 else paper_context
            
            prompt = f"""You are analyzing Figure {image_number} from a scientific research paper.

Paper Context (first 3000 chars):
---
{context_preview}
---

Image Format: {image_info['format']}
Alt Text: {image_info.get('alt_text', 'N/A')}

Please analyze this image thoroughly and provide:

1. title: A descriptive title for this image (e.g., "Patient Flow Diagram", "Treatment Outcomes Chart", "Microscopy Image")
2. image_type: The type of image (chart, graph, diagram, flowchart, microscopy, photograph, schematic, etc.)
3. description: A detailed description of what the image contains - describe all visible elements, data, labels, trends, and visual features in detail
4. statistical_analysis: If the image contains statistical data, charts, or graphs, describe the statistical information, trends, comparisons, p-values, confidence intervals, or any quantitative findings shown
5. keywords: 10-15 relevant keywords including image type, medical/scientific terms, data types, methodology terms, and concepts that would help someone search for this image

Focus on the scientific content and interpret the visual data in the context of the research study.

Return ONLY a valid JSON object with these exact fields: 'title', 'image_type', 'description', 'statistical_analysis', 'keywords'
Do not include any explanatory text, just the JSON object."""

            # Create the content with proper format for multimodal input
            content = {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": f"image/{image_info['format']}",
                            "data": image_info['data']  # Use base64 string directly
                        }
                    }
                ]
            }
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",  # Using vision-capable model
                contents=[content],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )
            
            if response.text:
                try:
                    # Parse JSON response
                    analysis = json.loads(response.text)
                    
                    # Validate required fields
                    required_fields = ['title', 'image_type', 'description', 'statistical_analysis', 'keywords']
                    if all(field in analysis for field in required_fields):
                        return analysis
                    else:
                        print(f"✗ AI response missing required fields for image {image_number}")
                        return None
                    
                except json.JSONDecodeError as e:
                    print(f"✗ Error parsing AI response as JSON for image {image_number}: {e}")
                    return None
            else:
                print(f"✗ Empty response from AI for image {image_number}")
                return None
                
        except Exception as e:
            print(f"✗ Error during AI image analysis for image {image_number}: {e}")
            return None
    
    def extract_and_save_json(self, paper_content: str, output_file: str, source_file: str = "") -> bool:
        """
        Extract images and save as JSON file using AI analysis.
        
        Args:
            paper_content: Full content of the paper
            output_file: Path to save JSON output
            source_file: Source file path (optional)
            
        Returns:
            Boolean indicating success
        """
        try:
            images = self.extract_images(paper_content)
            
            if not images:
                print("✗ No images extracted to save")
                return False
            
            # Convert to JSON-serializable format
            images_data = []
            for image in images:
                images_data.append({
                    "id": image.id,
                    "paper_id": image.paper_id,
                    "image_number": image.image_number,
                    "title": image.title,
                    "image_type": image.image_type,
                    "format": image.format,
                    "base64_data": image.base64_data,
                    "description": image.description,
                    "statistical_analysis": image.statistical_analysis,
                    "keywords": image.keywords,
                    "width": image.width,
                    "height": image.height,
                    "extracted_at": image.extracted_at.isoformat()
                })
            
            # Save to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(images_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Successfully saved {len(images)} AI-analyzed images to {output_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving images to JSON: {e}")
            return False


# Example usage and testing function
def main():
    """
    Example usage of the AIImageExtractionAgent.
    
    This demonstrates how to use the agent following the project's patterns.
    """
    print("🚀 Testing AI Image Extraction Agent...")
    print("=" * 60)
    
    # Initialize agent
    agent = AIImageExtractionAgent()
    
    # Test with sample paper
    sample_paper_path = Path(__file__).parent.parent / "docs" / "zanella_2025-with-images.md"
    
    if sample_paper_path.exists():
        try:
            # Load paper content
            with open(sample_paper_path, 'r', encoding='utf-8') as f:
                paper_content = f.read()
            
            print(f"📄 Loaded paper: {sample_paper_path}")
            
            # Save to JSON (this will also extract and display basic info)
            output_file = Path(__file__).parent / "extracted_images.json"
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
