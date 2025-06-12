"""
AI-Powered Table Extraction Agent for Scientific Papers.

This experimental module extracts tables from scientific papers in markdown format,
using Google Generative AI for intelligent table analysis, summarization and keyword extraction.
Follows the project's OOP architecture and established AI patterns from ai_extractor.py and text_agent.py.
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


class TableData(BaseModel):
    """
    Model for extracted tables from scientific papers.
    
    This follows the project's Pydantic pattern for data validation
    and uses the established 64-bit ID system.
    """
    
    id: int = Field(..., description="64-bit unique identifier for this table")
    paper_id: Optional[int] = Field(None, description="64-bit ID of the parent paper if available")
    table_number: int = Field(..., description="Sequential order of this table in the document")
    title: str = Field(..., description="Title/caption of the table")
    raw_content: str = Field(..., description="Raw markdown table content")
    summary: str = Field(..., description="Comprehensive summary of what the table shows and represents")
    context_analysis: str = Field(..., description="Analysis of what the table means in the context of the paper")
    statistical_findings: str = Field(..., description="Statistical results, conclusions, or key findings from the table")
    keywords: List[str] = Field(default_factory=list, description="Key words and phrases derived from the table content")
    column_count: int = Field(0, description="Number of columns in the table")
    row_count: int = Field(0, description="Number of rows in the table (excluding header)")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    @classmethod
    def generate_table_id(cls, title: str, content: str, table_number: int) -> int:
        """
        Generate a 64-bit ID for a table.
        
        Args:
            title: Table title/caption
            content: Table content
            table_number: Sequential position in document
            
        Returns:
            64-bit integer ID
        """
        # Create unique input combining all table identifiers
        unique_input = f"table_{table_number}:{title}:{content[:500]}"
        return generate_64bit_id(unique_input, f"table_{table_number}")


class AITableExtractionAgent:
    """
    AI-powered agent for extracting and analyzing tables from scientific papers.
    
    This class follows the project's OOP patterns from ai_extractor.py and text_agent.py with:
    - Single responsibility (table extraction and AI analysis)
    - Robust error handling with boolean return values
    - Google Generative AI integration following established patterns
    - AI-driven table content analysis and interpretation
    """
    
    def __init__(self):
        """Initialize the AI-powered table extraction agent following established patterns."""
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
        
        print("✓ AI-powered table extraction agent initialized")
        
    def _initialize_client(self) -> None:
        """Initialize the Google Generative AI client following established pattern."""
        try:
            self.client = genai.Client()
            print("✓ Google GenAI client initialized successfully for table analysis.")
        except Exception as e:
            print(f"✗ Error initializing Google GenAI client: {e}")
            print("Please ensure the GOOGLE_API_KEY environment variable is set and valid.")
            self.client = None
    
    def extract_tables(self, paper_content: str, source_file: str = "") -> List[TableData]:
        """
        Extract tables from paper content using AI for intelligent analysis.
        
        Args:
            paper_content: Full content of the paper in markdown format
            source_file: Source file path (optional, for better ID generation)
            
        Returns:
            List of TableData objects with AI-generated analysis
        """
        if not self.client:
            print("✗ AI client not available. Cannot proceed with intelligent table extraction.")
            return []
        
        try:
            print("🔍 Starting AI-powered table extraction...")
            
            # First, extract raw tables using regex
            raw_tables = self._extract_raw_tables_from_markdown(paper_content)
            
            if not raw_tables:
                print("✗ No tables found in markdown content")
                return []
            
            print(f"📊 Found {len(raw_tables)} raw tables, analyzing with AI...")
            
            # Use AI to analyze each table
            table_data_list = []
            for i, raw_table in enumerate(raw_tables, 1):
                try:
                    # Get AI analysis for this table
                    analysis = self._ai_analyze_table(raw_table, paper_content, i)
                    
                    if analysis:
                        # Create TableData object
                        table_data = TableData(
                            id=TableData.generate_table_id(analysis.get('title', f'Table {i}'), raw_table, i),
                            paper_id=None,  # Will be set when integrated with paper processing
                            table_number=i,
                            title=analysis.get('title', f'Table {i}'),
                            raw_content=raw_table,
                            summary=analysis.get('summary', ''),
                            context_analysis=analysis.get('context_analysis', ''),
                            statistical_findings=analysis.get('statistical_findings', ''),
                            keywords=analysis.get('keywords', []),
                            column_count=self._count_columns(raw_table),
                            row_count=self._count_rows(raw_table),
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
            print(f"✗ Error during AI-powered table extraction: {e}")
            return []
    
    def _extract_raw_tables_from_markdown(self, content: str) -> List[str]:
        """
        Extract raw table content from markdown using regex.
        
        Args:
            content: Full markdown content
            
        Returns:
            List of raw table strings
        """
        try:
            # Regex pattern to match markdown tables
            # This matches tables with headers and data rows
            table_pattern = r'(\|[^\n]+\|\n\|[-|\s:]+\|\n(?:\|[^\n]+\|\n?)*)'
            
            tables = re.findall(table_pattern, content, re.MULTILINE)
            
            # Clean up tables and filter out very small ones
            cleaned_tables = []
            for table in tables:
                table = table.strip()
                # Only include tables with at least 2 rows (header + data)
                if table.count('\n') >= 2 and table.count('|') > 6:
                    cleaned_tables.append(table)
            
            return cleaned_tables
            
        except Exception as e:
            print(f"✗ Error extracting raw tables: {e}")
            return []
    
    def _count_columns(self, table_content: str) -> int:
        """Count the number of columns in a markdown table."""
        try:
            # Get the first row to count columns
            first_row = table_content.split('\n')[0]
            # Count pipe characters and subtract 1 (for the leading/trailing pipes)
            return max(0, first_row.count('|') - 1)
        except:
            return 0
    
    def _count_rows(self, table_content: str) -> int:
        """Count the number of data rows in a markdown table (excluding header and separator)."""
        try:
            lines = table_content.split('\n')
            # Subtract header row and separator row
            return max(0, len([line for line in lines if line.strip() and '|' in line]) - 2)
        except:
            return 0
    
    def _ai_analyze_table(self, table_content: str, paper_context: str, table_number: int) -> Optional[Dict[str, Any]]:
        """
        Use AI to analyze a single table in the context of the paper.
        
        Args:
            table_content: Raw markdown table content
            paper_context: Full paper content for context
            table_number: Sequential number of this table
            
        Returns:
            Dictionary with analysis results or None if failed
        """
        try:
            if not self.client:
                print(f"✗ AI client not available for table {table_number} analysis")
                return None
                
            # Truncate paper context to avoid token limits
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

Analyze this table thoroughly and provide:

1. title: A descriptive title for this table (e.g., "Patient Demographics", "Treatment Outcomes", "Statistical Results")
2. summary: A comprehensive 2-3 sentence summary describing what data the table contains and what it shows
3. context_analysis: Explain what this table means in the context of the research paper - how does it support the study's objectives?
4. statistical_findings: Identify any statistical results, p-values, confidence intervals, significant findings, or key conclusions that can be drawn from the data
5. keywords: 10-15 relevant keywords including statistical terms, medical/scientific concepts, variable names, and methodology terms that would help someone search for this table

Focus on the research significance and interpret the data in the context of the study.

Return ONLY a valid JSON object with these exact fields: 'title', 'summary', 'context_analysis', 'statistical_findings', 'keywords'
Do not include any explanatory text, just the JSON object."""

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
    
    def extract_and_save_json(self, paper_content: str, output_file: str, source_file: str = "") -> bool:
        """
        Extract tables and save as JSON file using AI analysis.
        
        Args:
            paper_content: Full content of the paper
            output_file: Path to save JSON output
            source_file: Source file path (optional)
            
        Returns:
            Boolean indicating success
        """
        try:
            tables = self.extract_tables(paper_content, source_file)
            
            if not tables:
                print("✗ No tables extracted to save")
                return False
            
            # Convert to JSON-serializable format
            tables_data = []
            for table in tables:
                tables_data.append({
                    "id": table.id,
                    "paper_id": table.paper_id,
                    "table_number": table.table_number,
                    "title": table.title,
                    "raw_content": table.raw_content,
                    "summary": table.summary,
                    "context_analysis": table.context_analysis,
                    "statistical_findings": table.statistical_findings,
                    "keywords": table.keywords,
                    "column_count": table.column_count,
                    "row_count": table.row_count,
                    "extracted_at": table.extracted_at.isoformat()
                })
            
            # Save to JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tables_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Successfully saved {len(tables)} AI-analyzed tables to {output_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving tables to JSON: {e}")
            return False


# Example usage and testing function
def main():
    """
    Example usage of the AITableExtractionAgent.
    
    This demonstrates how to use the agent following the project's patterns.
    """
    print("🚀 Testing AI Table Extraction Agent...")
    print("=" * 60)
    
    # Initialize agent
    agent = AITableExtractionAgent()
    
    # Test with sample paper
    sample_paper_path = Path(__file__).parent.parent / "docs" / "zanella_2025-with-images.md"
    
    if sample_paper_path.exists():
        try:
            # Load paper content
            with open(sample_paper_path, 'r', encoding='utf-8') as f:
                paper_content = f.read()
            
            print(f"📄 Loaded paper: {sample_paper_path}")
            
            # Save to JSON (this will also extract and display basic info)
            output_file = Path(__file__).parent / "extracted_tables.json"
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
