"""
AI-Powered Image Extraction Agent for Scientific Papers.

This module extracts images from scientific papers in markdown format,
using Google Generative AI for intelligent image analysis, description and keyword extraction.
Follows the project's OOP architecture and established AI patterns.
"""

import os
import json
import re
import base64
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import the existing models and AI model configuration
from ..models.image_data import ImageData
from ..config.ai_models import AI_MODELS


class ImageExtractor:
    """
    AI-powered agent for extracting and analyzing images from scientific papers.
    
    This class follows the project's OOP patterns with:
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
        
        # Define model configuration once - single source of truth
        self.model_name = AI_MODELS.get_model_for_agent('default')
        self.temperature = AI_MODELS.DEFAULT_TEMPERATURE
        self.max_tokens = AI_MODELS.DEFAULT_MAX_TOKENS
        
        # Initialize the AI client following established pattern
        self.client = None
        self._initialize_client()
        
        # Print model configuration for transparency
        print(f"✓ AI-powered image extraction agent initialized using model: {self.model_name}")
        print(f"  Temperature: {self.temperature}, Max tokens: {self.max_tokens}")
        
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
            
            # Extract raw images using regex
            raw_images = self._extract_raw_images_from_markdown(paper_content)
            
            if not raw_images:
                print("✗ No images found in markdown content")
                return []
            
            print(f"🖼️  Found {len(raw_images)} raw images, analyzing with AI...")
            
            # Process each image with AI
            image_data_list = []
            for i, (alt_text, image_data, image_format) in enumerate(raw_images, 1):
                try:
                    # Get AI analysis for this image
                    analysis = self._ai_analyze_image(image_data, alt_text, paper_content, i, image_format)
                    
                    if analysis:
                        # Create ImageData object
                        image_obj = ImageData(
                            id=ImageData.generate_image_id(alt_text, image_data, i),
                            paper_id=paper_id,
                            image_number=i,
                            alt_text=alt_text,
                            image_data=image_data,
                            image_format=image_format,
                            summary=analysis.get('summary', ''),
                            graphic_analysis=analysis.get('graphic_analysis', ''),
                            statistical_analysis=analysis.get('statistical_analysis', ''),
                            contextual_relevance=analysis.get('contextual_relevance', ''),
                            keywords=analysis.get('keywords', [])
                        )
                        image_data_list.append(image_obj)
                        print(f"  ✓ Image {i}: '{alt_text[:50]}...' analyzed with AI")
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
    
    def _extract_raw_images_from_markdown(self, content: str) -> List[tuple]:
        """
        Extract raw image data from markdown using regex patterns.
        
        Args:
            content: Full markdown content
            
        Returns:
            List of tuples (alt_text, image_data, image_format)
        """
        try:
            # Regex pattern to match markdown images with base64 data
            # Matches: ![alt text](data:image/format;base64,data)
            image_pattern = r'!\[([^\]]*)\]\(data:image/([^;]+);base64,([^)]+)\)'
            
            matches = re.findall(image_pattern, content, re.MULTILINE | re.DOTALL)
            
            # Process matches and validate base64 data
            valid_images = []
            for alt_text, image_format, base64_data in matches:
                # Clean up base64 data (remove whitespace and newlines)
                cleaned_data = re.sub(r'\s+', '', base64_data)
                
                # Basic validation: check if it looks like valid base64 and supported format
                if (len(cleaned_data) > 100 and 
                    self._is_valid_base64(cleaned_data) and 
                    self._validate_image_format(image_format)):
                    valid_images.append((
                        alt_text.strip() if alt_text else f"Image {len(valid_images) + 1}",
                        cleaned_data,
                        image_format.lower()
                    ))
                else:
                    if not self._validate_image_format(image_format):
                        print(f"⚠️  Skipping unsupported image format: {image_format}")
                    else:
                        print(f"⚠️  Skipping invalid or too small image data (length: {len(cleaned_data)})")
                        
            
            return valid_images
            
        except Exception as e:
            print(f"✗ Error extracting raw images: {e}")
            return []
    
    def _is_valid_base64(self, data: str) -> bool:
        """
        Check if a string is valid base64 data.
        
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
    
    def _ai_analyze_image(self, image_data: str, alt_text: str, paper_context: str, 
                         image_number: int, image_format: str) -> Optional[Dict[str, Any]]:
        """
        Use AI to analyze an image in the context of the research paper.
        
        Args:
            image_data: Base64 encoded image data
            alt_text: Alt text or caption for the image
            paper_context: Full paper content for context
            image_number: Sequential number of this image
            image_format: Image format (png, jpg, etc.)
            
        Returns:
            Dictionary with analysis results or None if analysis failed
        """
        try:
            if not self.client:
                print(f"✗ AI client not available for image {image_number} analysis")
                return None
            
            # Truncate paper context to avoid token limits while preserving context
            context_preview = paper_context[:3000] + "..." if len(paper_context) > 3000 else paper_context
            
            # Create the image data for AI analysis using Gemini API best practices
            try:
                # Decode the base64 data to bytes for the API
                image_bytes = base64.b64decode(image_data)
                
                # Validate image size (Gemini API best practices)
                image_size_mb = len(image_bytes) / (1024 * 1024)
                if image_size_mb > 15:  # Stay well under 20MB limit
                    print(f"⚠️  Image {image_number} is large ({image_size_mb:.1f}MB), processing may be slower")
                
                # Get proper MIME type
                proper_mime_type = self._get_proper_mime_type(image_format)
                
                # Create the image part using the Gemini API recommended approach
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=proper_mime_type
                )
                
            except Exception as e:
                print(f"✗ Error processing image data for image {image_number}: {e}")
                return None
            
            # Construct prompt following best practices for image understanding
            prompt = f"""You are analyzing Image {image_number} from a scientific research paper.

Paper Context (first 3000 chars):
---
{context_preview}
---

Image Alt Text/Caption: "{alt_text}"
Image Format: {image_format}

Analyze this image thoroughly in the context of the research paper and provide:

1. summary: A comprehensive 3-4 sentence description of what the image contains, including visual elements, text, charts, diagrams, or photographs
2. graphic_analysis: Detailed analysis of the graphic type (e.g., bar chart, line graph, flowchart, microscopy image, diagram, photograph) and describe all visual elements, axes, legends, data points, patterns, and structure
3. statistical_analysis: If the image contains statistical data, charts, or graphs, analyze the statistical content, trends, significant findings, p-values, confidence intervals, or data patterns. If no statistical content, state "No statistical content identified"
4. contextual_relevance: Explain how this image relates to and supports the research objectives, methodology, or findings described in the paper context
5. keywords: 10-15 relevant keywords including image type, data visualization terms, scientific concepts, methodology terms, and domain-specific terminology that would help someone search for this image

Focus on scientific accuracy and detail. Be specific about visual elements and their meaning.

Return ONLY a valid JSON object with these exact fields: 'summary', 'graphic_analysis', 'statistical_analysis', 'contextual_relevance', 'keywords'
Do not include any explanatory text, just the JSON object."""

            # Make API call following Gemini image understanding best practices
            print(f"  🤖 Analyzing image {image_number} with model: {self.model_name}")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    image_part,  # Image first
                    prompt       # Text prompt after image
                ],
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    response_mime_type="application/json",
                ),
            )
            
            if response.text:
                try:
                    # Parse JSON response
                    analysis = json.loads(response.text)
                    
                    # Validate required fields
                    required_fields = ['summary', 'graphic_analysis', 'statistical_analysis', 
                                     'contextual_relevance', 'keywords']
                    if all(field in analysis for field in required_fields):
                        # Ensure keywords is always a list
                        if isinstance(analysis['keywords'], str):
                            # If keywords is a string, split it into a list
                            analysis['keywords'] = [kw.strip() for kw in analysis['keywords'].split(',')]
                        elif not isinstance(analysis['keywords'], list):
                            # If keywords is neither string nor list, default to empty list
                            analysis['keywords'] = []
                        
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
    
    def _validate_image_format(self, image_format: str) -> bool:
        """
        Validate if the image format is supported by Gemini API.
        
        Args:
            image_format: Image format string to validate
            
        Returns:
            True if format is supported, False otherwise
        """
        supported_formats = {'png', 'jpg', 'jpeg', 'webp', 'heic', 'heif'}
        return image_format.lower() in supported_formats
        
    def _get_proper_mime_type(self, image_format: str) -> str:
        """
        Get the proper MIME type for an image format.
        
        Args:
            image_format: Image format (e.g., 'jpg', 'png')
            
        Returns:
            Proper MIME type string
        """
        mime_type_mapping = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg', 
            'png': 'image/png',
            'webp': 'image/webp',
            'heic': 'image/heic',
            'heif': 'image/heif'
        }
        return mime_type_mapping.get(image_format.lower(), f'image/{image_format}')
