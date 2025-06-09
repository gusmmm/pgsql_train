from google import genai
from google.genai import types  # Import the 'types' module
from pydantic import BaseModel, Field
# Added imports for type hinting and datetime
from typing import List, Optional
from datetime import datetime
import json # For JSON parsing and pretty-printing

# Define the PaperMetadata class for schema-based response
# This class structure guides the LLM on how to format the extracted metadata.
class PaperMetadata(BaseModel):
    """Enhanced metadata model for scientific papers."""
    # Core identification and bibliographic information
    id: int = Field(..., description="64-bit unique identifier for the paper")
    title: str = Field(..., description="Title of the paper")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    journal: Optional[str] = Field(None, description="Journal name")
    publication_date: Optional[str] = Field(None, description="Publication date")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    volume: Optional[str] = Field(None, description="Journal volume")
    issue: Optional[str] = Field(None, description="Journal issue")
    pages: Optional[str] = Field(None, description="Page range")
    abstract: Optional[str] = Field(None, description="Paper abstract")
    keywords: List[str] = Field(default_factory=list, description="List of keywords")
    
    # Source and extraction timestamp
    source_file: str = Field(..., description="Source file path or name")
    extracted_at: datetime = Field(default_factory=datetime.now, description="Timestamp of extraction")
    
    # Enhanced fields for medical research context
    paper_type: str = Field(default="research_article", description="Type of paper (research_article, review, case_study, etc.)")
    study_design: Optional[str] = Field(None, description="Study design (cohort, RCT, observational, etc.)")
    medical_specialty: Optional[str] = Field(None, description="Medical specialty or field")
    study_population: Optional[str] = Field(None, description="Description of study population")
    study_period: Optional[str] = Field(None, description="Study period or timeframe")
    
    # Funding and ethical considerations
    funding_sources: List[str] = Field(default_factory=list, description="Funding sources")
    conflict_of_interest: Optional[str] = Field(None, description="Conflict of interest statement")
    data_availability: Optional[str] = Field(None, description="Data availability statement")
    ethics_approval: Optional[str] = Field(None, description="Ethics approval information")
    registration_number: Optional[str] = Field(None, description="Clinical trial registration number")
    
    # Supplemental materials
    supplemental_materials: List[str] = Field(default_factory=list, description="List of supplemental materials")

# Path to the medical paper to be processed
PAPER_FILE_PATH = "/home/gusmmm/Desktop/public_repos/pgsql_train/docs/zanella_2025-with-images.md"

# Attempt to read the content of the specified paper
try:
    with open(PAPER_FILE_PATH, 'r', encoding='utf-8') as f:
        paper_content = f.read()
    # Log success or basic info about the paper loaded
    print(f"Successfully loaded paper content from: {PAPER_FILE_PATH}")
except FileNotFoundError:
    # Handle cases where the paper file does not exist
    print(f"Error: Paper file not found at {PAPER_FILE_PATH}")
    paper_content = None # Ensure paper_content is defined for subsequent checks
except Exception as e:
    # Handle other potential errors during file reading
    print(f"Error reading paper file '{PAPER_FILE_PATH}': {e}")
    paper_content = None

# Proceed only if paper content was successfully loaded
if paper_content:
    # Initialize the Google Generative AI client
    # This assumes GOOGLE_API_KEY is set in the environment variables
    try:
        client = genai.Client()
        print("Google GenAI client initialized successfully.")
    except Exception as e:
        # Handle errors during client initialization, often related to API key issues
        print(f"Error initializing Google GenAI client: {e}")
        print("Please ensure the GOOGLE_API_KEY environment variable is set and valid.")
        client = None # Ensure client is defined for subsequent checks

    if client:
        # Construct the prompt for the language model, including the paper content
        # This prompt guides the model to extract metadata according to the PaperMetadata schema
        # The f-string uses """ for multiline string compatibility within the tool's code argument.
        prompt_for_llm = f"""Please extract metadata from the following medical research paper.
The output must be a JSON object that strictly conforms to the PaperMetadata schema provided to you.
Do not change the schema or add any additional fields.
Do not change the content of the fields or the Paper Content, just extract the information as accurately as possible.
Key instructions for specific fields:
- 'id': Generate a simple integer (e.g., 1 or a hash if possible, but 1 is acceptable for this test) if no specific ID is found in the text.
- 'source_file': This field must be exactly: "{PAPER_FILE_PATH}"
- 'extracted_at': This field should represent the current timestamp when you process this (e.g., {datetime.now().isoformat()}).
- For other fields, extract them from the paper content. If a field is not present, omit it if it's Optional, or use an appropriate default if specified in the schema.

Paper Content:
---
{paper_content}
---
"""
        print("Prompt constructed for LLM.")

        # Call the generative model to extract metadata
        try:
            print(f"Sending request to model: gemini-2.5-flash-preview-05-20 with PaperMetadata schema.")
            response = client.models.generate_content(
                #model="gemini-2.5-flash-preview-05-20",
                model="gemini-2.5-pro-preview-06-05",  # Specify the model to use
                contents=prompt_for_llm,
                # Use types.GenerateContentConfig for schema-based response and other parameters
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PaperMetadata,
                    temperature=0.1,  # Added temperature setting (adjust as needed)
                ),
            )
            print("Received response from LLM.")

            # The response.text is expected to be a JSON string matching the PaperMetadata schema
            extracted_metadata_json_str = response.text

            # Attempt to parse the JSON string and print it in a readable format
            if extracted_metadata_json_str:
                try:
                    metadata_dict = json.loads(extracted_metadata_json_str)
                    print("\nExtracted Metadata (Formatted JSON):\n")
                    # Output the extracted metadata as a formatted JSON string
                    print(json.dumps(metadata_dict, indent=2))
                except json.JSONDecodeError as e:
                    # Handle cases where the LLM response is not valid JSON
                    print(f"\nError decoding JSON from LLM response: {e}")
                    print("Raw response text was:")
                    print(extracted_metadata_json_str)
                except Exception as pydantic_error:
                    # Handle other errors, e.g., if Pydantic validation (if explicitly used) fails
                    print(f"\nError processing/validating metadata: {pydantic_error}")
                    print("Raw response text was:")
                    print(extracted_metadata_json_str)
            else:
                print("\nLLM response was empty.")

        except Exception as e:
            # Handle errors during the API call to the generative model
            print(f"\nAn error occurred during content generation with the LLM: {e}")
            # Attempt to print more detailed error information if available
            if hasattr(e, 'args') and e.args:
                print(f"Error details: {e.args[0] if e.args else 'No specific details'}")
            # For genai specific errors, they might have a different structure
            # This is a generic way to access common error attributes if they exist
            # For specific API error handling, consult the google.generativeai documentation
            # For example, some Google API errors might have a `response` attribute with more info
            # but this is not standard for all Exceptions.
    else:
        # Message if client initialization failed
        print("Google GenAI client not initialized. Cannot proceed with metadata extraction.")
else:
    # Message if paper content could not be loaded
    print("Paper content not loaded. Cannot proceed with metadata extraction.")

# The original client instantiation, generate_content call, and print statement 
# from the initial paper_agent.py are effectively replaced by the comprehensive logic above.