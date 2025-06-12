"""
Main paper processing pipeline using refactored OOP structure.

This module provides the PaperProcessor class that orchestrates the complete
paper processing workflow using the refactored components.
"""

import os
import sys
from typing import Optional, Tuple

from .models import PaperMetadata, TextSection
from .extraction import AIExtractor, TextExtractor
from .database import DatabaseConnection, SchemaManager, PaperMetadataRepository, TextSectionsRepository
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
        self.text_sections_repository = TextSectionsRepository(self.db_connection, schema_name)
        self.extractor = AIExtractor()
        self.text_extractor = TextExtractor()
        
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
            
            # Step 5: Check for duplicate papers and get user preference
            print("\n🔍 Step 5: Checking for duplicate papers...")
            exists, should_overwrite = self._check_paper_exists(paper_metadata)
            
            if exists and not should_overwrite:
                print("⏭️  Skipping processing - keeping existing paper.")
                return True
            
            # Step 6: Handle overwrite if needed
            if exists and should_overwrite:
                print("\n🔄 Step 6: Cleaning up existing data for overwrite...")
                # Delete existing text sections first (due to foreign key constraint)
                if self.text_sections_repository.exists_by_paper_id(paper_metadata.id):
                    print("   Deleting existing text sections...")
                    self.text_sections_repository.delete_by_paper_id(paper_metadata.id)
            
            # Step 7: Insert/Update paper metadata
            print(f"\n💾 Step 7: {'Updating' if exists and should_overwrite else 'Inserting'} paper metadata...")
            success = self._save_paper_metadata(paper_metadata, update_existing=exists and should_overwrite)
            if not success:
                return False
            
            # Step 8: Extract and save text sections
            print("\n📝 Step 8: Extracting text sections using AI...")
            text_sections = self.text_extractor.extract_text_sections(paper_content, paper_metadata.id)
            
            if text_sections:
                print("\n💾 Step 9: Saving text sections to database...")
                sections_success = self.text_sections_repository.save_all(text_sections)
                if not sections_success:
                    print("⚠️  Warning: Failed to save some text sections")
            else:
                print("⚠️  Warning: No text sections extracted")
            
            # Commit the transaction
            if self.db_connection.connection:
                self.db_connection.connection.commit()
                
            print("\n" + "=" * 60)
            print("🎉 Paper processing completed successfully!")
            print(f"   📄 Paper metadata: {'Updated' if exists else 'Inserted'}")
            print(f"   📝 Text sections: {len(text_sections)} sections processed")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n✗ Critical error in paper processing pipeline: {e}")
            # Rollback on error
            if self.db_connection.connection:
                self.db_connection.connection.rollback()
            return False
            
        finally:
            self.close_connections()
    
    def _check_paper_exists(self, paper_metadata: PaperMetadata) -> Tuple[bool, bool]:
        """
        Check if paper already exists in database and ask user preference.
        
        Args:
            paper_metadata: Paper metadata to check
            
        Returns:
            Tuple of (exists, should_overwrite)
        """
        doi = paper_metadata.doi
        title = paper_metadata.title
        existing_paper = None
        
        if doi:
            # Check by DOI first (most reliable)
            existing_paper = self.repository.find_by_doi(doi)
            if existing_paper:
                print(f"📄 Paper already exists in database:")
                print(f"   ID: {existing_paper['id']}")
                print(f"   Title: {existing_paper['title']}")
                print(f"   DOI: {existing_paper['doi']}")
        
        if not existing_paper and title:
            # If no DOI match, check by exact title match
            existing_paper = self.repository.find_by_title(title)
            if existing_paper:
                print(f"📄 Paper with same title already exists in database:")
                print(f"   ID: {existing_paper['id']}")
                print(f"   Title: {existing_paper['title']}")
                print(f"   DOI: {existing_paper['doi']}")
        
        if existing_paper:
            # Ask user what to do
            print("\n❓ What would you like to do?")
            print("   1. Skip processing (keep existing paper)")
            print("   2. Overwrite existing paper and its text sections")
            
            while True:
                try:
                    choice = input("Enter choice (1 or 2): ").strip()
                    if choice == "1":
                        return True, False  # exists, don't overwrite
                    elif choice == "2":
                        # Store paper ID for potential text sections cleanup
                        paper_metadata.id = existing_paper['id']
                        return True, True  # exists, overwrite
                    else:
                        print("Invalid choice. Please enter 1 or 2.")
                except KeyboardInterrupt:
                    print("\n⏭️  Operation cancelled. Skipping paper processing.")
                    return True, False
        
        return False, False  # doesn't exist
    
    def _save_paper_metadata(self, paper_metadata: PaperMetadata, update_existing: bool = False) -> bool:
        """
        Save paper metadata to database.
        
        Args:
            paper_metadata: Paper metadata to save
            update_existing: If True, update existing record; if False, insert new record
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if update_existing:
                return self.repository.update(paper_metadata)
            else:
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
