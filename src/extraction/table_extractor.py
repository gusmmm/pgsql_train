"""
Table Extraction Module for Scientific Paper Processing System.

This module provides AI-powered table extraction capabilities for scientific papers,
following the project's established patterns for extraction, analysis, and data validation.
"""

import os
import json
import re
from typing import List, Optional, Dict, Any
from google import genai
from google.genai import types
from dotenv import load_dotenv

from ..models.table_data import TableData
from ..config.ai_models import AI_MODELS


class TableExtractor:
    """
    AI-powered table extraction service for scientific papers.
    
    This class follows the project's established patterns from ai_extractor.py and text_extractor.py,
    providing single-responsibility table extraction with comprehensive AI analysis.
    
    Key Features:
    - Regex-based markdown table detection
    - AI-powered content analysis and interpretation  
    - Structured data output with comprehensive metadata
    - Robust error handling with clear success indicators
    - Integration with existing 64-bit ID system
    """
    
    def __init__(self):
        """
        Initialize the table extractor with Google GenAI client.
        
        Follows the established pattern from ai_extractor.py for consistent
        initialization and error handling.
        """
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
        
        # Print model configuration for transparency
        print(f"✓ Table Extractor initialized using model: {AI_MODELS.get_model_for_agent('table')}")
        print(f"  Temperature: {AI_MODELS.DEFAULT_TEMPERATURE}, Max tokens: {AI_MODELS.DEFAULT_MAX_TOKENS}")
        
    def _initialize_client(self) -> None:
        """Initialize the Google Generative AI client following established patterns."""
        try:
            self.client = genai.Client()
            print("✓ Google GenAI client initialized successfully for table extraction.")
        except Exception as e:
            print(f"✗ Error initializing Google GenAI client: {e}")
            print("Please ensure the API key environment variable is set and valid.")
            self.client = None
    
    def extract_tables(self, paper_content: str, paper_id: Optional[int] = None) -> List[TableData]:
        """
        Extract and analyze tables from paper content using AI.
        
        Args:
            paper_content: Full markdown content of the paper
            paper_id: Optional paper ID to link tables to their parent paper
            
        Returns:
            List of TableData objects with comprehensive AI analysis
        """
        if not self.client:
            print("✗ AI client not available. Cannot proceed with table extraction.")
            return []
        
        try:
            print("🔍 Starting AI-powered table extraction...")
            
            # Extract raw tables using regex
            raw_tables = self._extract_raw_tables_from_markdown(paper_content)
            
            if not raw_tables:
                print("✗ No tables found in markdown content")
                return []
            
            print(f"📊 Found {len(raw_tables)} raw tables, analyzing with AI...")
            
            # Process each table with AI
            table_data_list = []
            for i, raw_table in enumerate(raw_tables, 1):
                try:
                    # Get AI analysis for this table
                    analysis = self._ai_analyze_table(raw_table, paper_content, i)
                    
                    if analysis:
                        # Create TableData object
                        table_data = TableData(
                            id=TableData.generate_table_id(
                                analysis.get('title', f'Table {i}'), 
                                raw_table, 
                                i
                            ),
                            paper_id=paper_id,
                            table_number=i,
                            title=analysis.get('title', f'Table {i}'),
                            raw_content=raw_table,
                            summary=analysis.get('summary', ''),
                            context_analysis=analysis.get('context_analysis', ''),
                            statistical_findings=analysis.get('statistical_findings', ''),
                            keywords=analysis.get('keywords', []),
                            column_count=self._count_columns(raw_table),
                            row_count=self._count_rows(raw_table)
                        )
                        table_data_list.append(table_data)
                        print(f"  ✓ Table {i}: '{table_data.title[:50]}...' analyzed with AI")
                    else:
                        print(f"  ✗ Table {i}: AI analysis failed")
                        
                except Exception as e:
                    print(f"  ✗ Table {i}: Error during analysis: {e}")
                    continue
            
            print(f"✓ Successfully extracted and analyzed {len(table_data_list)} tables")
            return table_data_list
            
        except Exception as e:
            print(f"✗ Error during table extraction: {e}")
            return []
    
    def _extract_raw_tables_from_markdown(self, content: str) -> List[str]:
        """
        Extract raw table content from markdown using regex patterns.
        
        Args:
            content: Full markdown content
            
        Returns:
            List of raw table strings in markdown format
        """
        try:
            # Regex pattern to match complete markdown tables
            # Matches: header row | separator row | data rows
            table_pattern = r'(\|[^\n]+\|\n\|[-|\s:]+\|\n(?:\|[^\n]+\|\n?)*)'
            
            tables = re.findall(table_pattern, content, re.MULTILINE)
            
            # Filter and clean tables
            cleaned_tables = []
            for table in tables:
                table = table.strip()
                # Only include tables with meaningful content:
                # - At least 2 rows (header + data)
                # - Sufficient column structure (more than 6 pipe characters)
                if table.count('\n') >= 2 and table.count('|') > 6:
                    cleaned_tables.append(table)
            
            return cleaned_tables
            
        except Exception as e:
            print(f"✗ Error extracting raw tables: {e}")
            return []
    
    def _count_columns(self, table_content: str) -> int:
        """
        Count the number of columns in a markdown table.
        
        Args:
            table_content: Raw markdown table content
            
        Returns:
            Number of columns in the table
        """
        try:
            # Get the first row to count columns
            first_row = table_content.split('\n')[0]
            # Count pipe characters and subtract 1 (for leading/trailing pipes)
            return max(0, first_row.count('|') - 1)
        except:
            return 0
    
    def _count_rows(self, table_content: str) -> int:
        """
        Count the number of data rows in a markdown table.
        
        Args:
            table_content: Raw markdown table content
            
        Returns:
            Number of data rows (excluding header and separator)
        """
        try:
            lines = table_content.split('\n')
            # Count lines with pipe characters, then subtract header and separator
            data_lines = [line for line in lines if line.strip() and '|' in line]
            return max(0, len(data_lines) - 2)
        except:
            return 0
    
    def _ai_analyze_table(self, table_content: str, paper_context: str, table_number: int) -> Optional[Dict[str, Any]]:
        """
        Use AI to analyze a table in the context of the research paper.
        
        Args:
            table_content: Raw markdown table content
            paper_context: Full paper content for context
            table_number: Sequential number of this table
            
        Returns:
            Dictionary with analysis results or None if analysis failed
        """
        try:
            if not self.client:
                print(f"✗ AI client not available for table {table_number} analysis")
                return None
            
            # Truncate paper context to avoid token limits while preserving context
            context_preview = paper_context[:3000] + "..." if len(paper_context) > 3000 else paper_context
            
            prompt = f"""You are analyzing Table {table_number} from a scientific research paper. 

Paper Context (first 3000 chars):
---
{context_preview}
---

Table {table_number} Content:
---
{table_content}
---

Analyze this table thoroughly and provide a comprehensive analysis:

1. title: A descriptive title for this table (e.g., "Patient Demographics", "Treatment Outcomes", "Statistical Results")
2. summary: A comprehensive 2-3 sentence summary describing what data the table contains and what it shows
3. context_analysis: Explain what this table means in the context of the research paper - how does it support the study's objectives and findings?
4. statistical_findings: Identify any statistical results, p-values, confidence intervals, significant findings, or key conclusions that can be drawn from the data
5. keywords: 10-15 relevant keywords including statistical terms, medical/scientific concepts, variable names, and methodology terms

Focus on the research significance and interpret the data in the context of the study.

Return ONLY a valid JSON object with these exact fields: 'title', 'summary', 'context_analysis', 'statistical_findings', 'keywords'
Do not include any explanatory text, just the JSON object."""

            model_name = AI_MODELS.get_model_for_agent('table')
            print(f"  🤖 Analyzing table {table_number} with model: {model_name}")
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=AI_MODELS.DEFAULT_TEMPERATURE,
                    response_mime_type="application/json",
                ),
            )
            
            if response.text:
                try:
                    # Parse JSON response
                    analysis = json.loads(response.text)
                    
                    # Validate required fields
                    required_fields = ['title', 'summary', 'context_analysis', 'statistical_findings', 'keywords']
                    if all(field in analysis for field in required_fields):
                        return analysis
                    else:
                        print(f"✗ AI response missing required fields for table {table_number}")
                        return None
                    
                except json.JSONDecodeError as e:
                    print(f"✗ Error parsing AI response as JSON for table {table_number}: {e}")
                    return None
            else:
                print(f"✗ Empty response from AI for table {table_number}")
                return None
                
        except Exception as e:
            print(f"✗ Error during AI table analysis for table {table_number}: {e}")
            return None
