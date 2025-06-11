"""
Main paper processing pipeline using refactored OOP structure.

This module provides the PaperProcessor class that orchestrates the complete
paper processing workflow using the refactored components.
"""

import os
import sys
from typing import Optional

from .models import PaperMetadata
from .extraction import AIExtractor
from .database import DatabaseConnection, SchemaManager, PaperMetadataRepository
from .utils import FileLoader


class PaperProcessor:
    """
    Main orchestrator for the paper processing pipeline.
    
    This class coordinates all components to provide a complete paper processing
    workflow from file loading to database storage.
    """
    
    def __init__(self, schema_name: str = 'papers'):
        """
        Initialize the paper processor.
        
        Args:
            schema_name: Name of the database schema to use
        """
        self.schema_name = schema_name
        
        # Initialize components
        self.db_connection = DatabaseConnection()
        self.schema_manager = SchemaManager(self.db_connection)
        self.repository = PaperMetadataRepository(self.db_connection, schema_name)
        self.extractor = AIExtractor()
        
        print(f"✓ Paper processor initialized with schema '{schema_name}'")
    
    def process_paper(self, paper_file_path: str) -> bool:
        """
        Process a single paper through the complete pipeline.
        
        Args:
            paper_file_path: Path to the paper file to process
            
        Returns:
            True if successful, False otherwise
        """
        print("🚀 Starting paper processing pipeline...")
        print("=" * 60)
        
        try:
            # Step 1: Validate and load paper content
            print("\n📖 Step 1: Loading paper content...")
            if not FileLoader.validate_file_exists(paper_file_path):
                print(f"✗ Error: Paper file does not exist: {paper_file_path}")
                return False
            
            paper_content = FileLoader.load_paper_content(paper_file_path)
            if not paper_content:
                print("✗ Failed to load paper content")
                return False
            
            # Step 2: Extract metadata using AI
            print("\n🤖 Step 2: Extracting metadata using AI...")
            paper_metadata = self.extractor.extract_metadata(paper_content, paper_file_path)
            if not paper_metadata:
                print("✗ Failed to extract metadata")
                return False
            
            # Step 3: Setup database connection and schema
            print("\n🗄️  Step 3: Setting up database connection...")
            self.db_connection.connect()
            
            print("\n📋 Step 4: Ensuring database schema exists...")
            self.schema_manager.setup_complete_schema(self.schema_name)
            
            # Step 5: Check for duplicate papers
            print("\n🔍 Step 5: Checking for duplicate papers...")
            if self._check_paper_exists(paper_metadata):
                print("⏭️  Skipping insertion - paper already exists in database.")
                return True
            
            # Step 6: Insert new paper
            print("\n💾 Step 6: Inserting paper metadata...")
            success = self._save_paper_metadata(paper_metadata)
            
            if success:
                # Commit the transaction
                if self.db_connection.connection:
                    self.db_connection.connection.commit()
                    
                print("\n" + "=" * 60)
                print("🎉 Paper processing completed successfully!")
                print("=" * 60)
            
            return success
            
        except Exception as e:
            print(f"\n✗ Critical error in paper processing pipeline: {e}")
            # Rollback on error
            if self.db_connection.connection:
                self.db_connection.connection.rollback()
            return False
            
        finally:
            self.close_connections()
    
    def _check_paper_exists(self, paper_metadata: PaperMetadata) -> bool:
        """
        Check if paper already exists in database.
        
        Args:
            paper_metadata: Paper metadata to check
            
        Returns:
            True if paper exists, False otherwise
        """
        doi = paper_metadata.doi
        title = paper_metadata.title
        
        if doi:
            # Check by DOI first (most reliable)
            existing_paper = self.repository.find_by_doi(doi)
            if existing_paper:
                print(f"📄 Paper already exists in database:")
                print(f"   ID: {existing_paper['id']}")
                print(f"   Title: {existing_paper['title']}")
                print(f"   DOI: {existing_paper['doi']}")
                return True
        
        if title:
            # If no DOI match, check by exact title match
            existing_paper = self.repository.find_by_title(title)
            if existing_paper:
                print(f"📄 Paper with same title already exists in database:")
                print(f"   ID: {existing_paper['id']}")
                print(f"   Title: {existing_paper['title']}")
                print(f"   DOI: {existing_paper['doi']}")
                return True
        
        return False
    
    def _save_paper_metadata(self, paper_metadata: PaperMetadata) -> bool:
        """
        Save paper metadata to database.
        
        Args:
            paper_metadata: Paper metadata to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.repository.save(paper_metadata)
        except Exception as e:
            print(f"✗ Error saving paper metadata: {e}")
            return False
    
    def list_papers(self) -> None:
        """List all papers in the database."""
        try:
            # Ensure connection
            if not self.db_connection.connection:
                self.db_connection.connect()
            
            papers = self.repository.find_all()
            
            if not papers:
                print("No papers found in the database.")
                return
            
            print(f"\n📚 Found {len(papers)} paper(s) in the database:")
            print("=" * 100)
            
            for i, paper in enumerate(papers, 1):
                print(f"\n{i}. Paper ID: {paper['id']}")
                print(f"   Title: {paper['title']}")
                print(f"   Authors: {', '.join(paper['first_authors']) if paper['first_authors'] else 'N/A'}")
                if paper['total_authors'] and paper['total_authors'] > 3:
                    print(f"            ... and {paper['total_authors'] - 3} more authors")
                print(f"   Journal: {paper['journal'] or 'N/A'}")
                print(f"   Publication Date: {paper['publication_date'] or 'N/A'}")
                print(f"   DOI: {paper['doi'] or 'N/A'}")
                print(f"   Extracted: {paper['extracted_at']}")
                print("-" * 100)
                
        except Exception as e:
            print(f"Error listing papers: {e}")
    
    def get_paper_details(self, paper_id: int) -> None:
        """
        Get detailed information about a specific paper.
        
        Args:
            paper_id: Paper ID to get details for
        """
        try:
            # Ensure connection
            if not self.db_connection.connection:
                self.db_connection.connect()
            
            paper = self.repository.find_by_id(paper_id)
            
            if not paper:
                print(f"No paper found with ID: {paper_id}")
                return
            
            print(f"\n📄 Paper Details:")
            print("=" * 80)
            print(f"ID: {paper['id']}")
            print(f"Title: {paper['title']}")
            print(f"Authors: {', '.join(paper['authors']) if paper['authors'] else 'N/A'}")
            print(f"Journal: {paper['journal'] or 'N/A'}")
            print(f"Publication Date: {paper['publication_date'] or 'N/A'}")
            print(f"DOI: {paper['doi'] or 'N/A'}")
            print(f"Volume: {paper['volume'] or 'N/A'}")
            print(f"Issue: {paper['issue'] or 'N/A'}")
            print(f"Pages: {paper['pages'] or 'N/A'}")
            print(f"Keywords: {', '.join(paper['keywords']) if paper['keywords'] else 'N/A'}")
            print(f"Source File: {paper['source_file']}")
            print(f"Extracted At: {paper['extracted_at']}")
            print(f"Created At: {paper['created_at']}")
            print(f"Updated At: {paper['updated_at']}")
            
            if paper['abstract']:
                print(f"\nAbstract:\n{paper['abstract']}")
            
            if paper['funding_sources']:
                print(f"\nFunding Sources:\n{', '.join(paper['funding_sources'])}")
            
            if paper['conflict_of_interest']:
                print(f"\nConflict of Interest:\n{paper['conflict_of_interest']}")
            
            if paper['data_availability']:
                print(f"\nData Availability:\n{paper['data_availability']}")
            
            if paper['ethics_approval']:
                print(f"\nEthics Approval:\n{paper['ethics_approval']}")
            
            if paper['registration_number']:
                print(f"\nRegistration Number: {paper['registration_number']}")
            
            if paper['supplemental_materials']:
                print(f"\nSupplemental Materials:")
                for i, material in enumerate(paper['supplemental_materials'], 1):
                    print(f"  {i}. {material}")
            
            print("=" * 80)
            
        except Exception as e:
            print(f"Error getting paper details: {e}")
    
    def close_connections(self) -> None:
        """Close database connections."""
        try:
            self.db_connection.disconnect()
        except Exception as e:
            print(f"Warning: Error closing database connections: {e}")


def main():
    """Main function to run the paper processor."""
    # Default paper file path
    default_paper_path = "/home/gusmmm/Desktop/pgsql_train/docs/zanella_2025-with-images.md"
    
    # Get paper file path from command line argument or use default
    if len(sys.argv) > 1:
        paper_file_path = sys.argv[1]
    else:
        paper_file_path = default_paper_path
    
    print(f"📄 Processing paper: {paper_file_path}")
    
    try:
        # Create and run processor
        processor = PaperProcessor()
        success = processor.process_paper(paper_file_path)
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
