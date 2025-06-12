"""
Main paper processing pipeline using refactored OOP structure.

This module provides the PaperProcessor class that orchestrates the complete
paper processing workflow using the refactored components.
"""

import os
import sys
from typing import Optional, Tuple, Dict, List

from .models import PaperMetadata, TextSection, TableData, ImageData
from .extraction import AIExtractor, TextExtractor, TableExtractor, ImageExtractor
from .database import DatabaseConnection, SchemaManager, PaperMetadataRepository, TextSectionsRepository, TableDataRepository, ImageRepository
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
        self.table_data_repository = TableDataRepository(self.db_connection, schema_name)
        self.image_repository = ImageRepository(self.db_connection, schema_name)
        self.extractor = AIExtractor()
        self.text_extractor = TextExtractor()
        self.table_extractor = TableExtractor()
        self.image_extractor = ImageExtractor()
        
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
            
            # Step 5: Check for duplicate papers and get user preferences
            print("\n🔍 Step 5: Checking for duplicate papers...")
            exists, overwrite_choices = self._check_paper_exists(paper_metadata)
            
            if exists and not any(overwrite_choices.values()):
                print("⏭️  Skipping processing - keeping all existing data.")
                return True
            
            # Step 6: Handle selective overwrite if needed
            if exists:
                print("\n🔄 Step 6: Cleaning up existing data for selective overwrite...")
                
                # Delete existing text sections if user chose to overwrite them
                if overwrite_choices.get('text_sections', False):
                    print("   Deleting existing text sections...")
                    self.text_sections_repository.delete_by_paper_id(paper_metadata.id)
                
                # Delete existing images if user chose to overwrite them
                if overwrite_choices.get('images', False):
                    print("   Deleting existing images...")
                    self.image_repository.delete_by_paper_id(paper_metadata.id)
                
                # Delete existing tables if user chose to overwrite them
                if overwrite_choices.get('tables', False):
                    print("   Deleting existing tables...")
                    self.table_data_repository.delete_tables_by_paper_id(paper_metadata.id)
            
            # Step 7: Insert/Update paper metadata if needed
            if not exists or overwrite_choices.get('metadata', False):
                print(f"\n💾 Step 7: {'Updating' if exists else 'Inserting'} paper metadata...")
                success = self._save_paper_metadata(paper_metadata, update_existing=exists)
                if not success:
                    return False
            else:
                print("\n⏭️  Step 7: Skipping paper metadata (keeping existing)")
            
            # Step 8: Extract and save text sections if needed
            if not exists or overwrite_choices.get('text_sections', False):
                print("\n📝 Step 8: Extracting text sections using AI...")
                text_sections = self.text_extractor.extract_text_sections(paper_content, paper_metadata.id)
                
                if text_sections:
                    print("\n💾 Step 9: Saving text sections to database...")
                    sections_success = self.text_sections_repository.save_all(text_sections)
                    if not sections_success:
                        print("⚠️  Warning: Failed to save some text sections")
                else:
                    print("⚠️  Warning: No text sections extracted")
            else:
                print("\n⏭️  Step 8-9: Skipping text sections (keeping existing)")
                text_sections = []
            
            # Step 10: Extract and save tables if needed
            if not exists or overwrite_choices.get('tables', False):
                print("\n📊 Step 10: Extracting tables using AI...")
                tables = self.table_extractor.extract_tables(paper_content, paper_metadata.id)
                
                if tables:
                    print("\n💾 Step 11: Saving tables to database...")
                    tables_success = self._save_all_tables(tables)
                    if not tables_success:
                        print("⚠️  Warning: Failed to save some tables")
                else:
                    print("⚠️  Warning: No tables found or extracted")
            else:
                print("\n⏭️  Step 10-11: Skipping tables (keeping existing)")
                tables = []
            
            # Step 12: Extract and save images if needed
            if not exists or overwrite_choices.get('images', False):
                print("\n🖼️  Step 12: Extracting images using AI...")
                images = self.image_extractor.extract_images(paper_content, paper_metadata.id)
                
                if images:
                    print("\n💾 Step 13: Saving images to database...")
                    images_success = self.image_repository.save_images(images)
                    if not images_success:
                        print("⚠️  Warning: Failed to save some images")
                else:
                    print("⚠️  Warning: No images found or extracted")
            else:
                print("\n⏭️  Step 12-13: Skipping images (keeping existing)")
                images = []
            
            # Commit the transaction
            if self.db_connection.connection:
                self.db_connection.connection.commit()
                
            print("\n" + "=" * 60)
            print("🎉 Paper processing completed successfully!")
            print(f"   📄 Paper metadata: {'Updated' if exists else 'Inserted'}")
            print(f"   📝 Text sections: {len(text_sections)} sections processed")
            print(f"   📊 Tables: {len(tables)} tables processed")
            print(f"   🖼️ Images: {len(images)} images processed")
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
    
    def process_images_only(self, paper_file_path: str) -> bool:
        """
        Process only images from a paper file.
        
        Args:
            paper_file_path: Path to the paper file to process
            
        Returns:
            True if successful, False otherwise
        """
        print("🚀 Starting image-only processing pipeline...")
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
            
            # Step 2: Setup database connection
            print("\n🗄️  Step 2: Setting up database connection...")
            self.db_connection.connect()
            
            print("\n📋 Step 3: Ensuring database schema exists...")
            self.schema_manager.setup_complete_schema(self.schema_name)
            
            # Step 4: Check if paper exists in database
            print("\n🔍 Step 4: Looking for existing paper in database...")
            
            # Try to find paper by filename first
            existing_paper = self.repository.find_by_source_file(paper_file_path)
            
            if not existing_paper:
                print("✗ Paper not found in database. Please process the paper metadata first using the main processor.")
                return False
            
            paper_id = existing_paper['id']
            print(f"✓ Found existing paper with ID: {paper_id}")
            print(f"   Title: {existing_paper['title']}")
            
            # Step 5: Check for existing images
            existing_images_count = len(self.image_repository.find_by_paper_id(paper_id))
            if existing_images_count > 0:
                print(f"\n⚠️  Found {existing_images_count} existing images for this paper.")
                overwrite = input("Do you want to overwrite existing images? (y/N): ").strip().lower()
                if overwrite in ['y', 'yes']:
                    print("   Deleting existing images...")
                    self.image_repository.delete_by_paper_id(paper_id)
                else:
                    print("   Skipping image processing to preserve existing data.")
                    return True
            
            # Step 6: Extract and save images
            print("\n🖼️  Step 6: Extracting images using AI...")
            images = self.image_extractor.extract_images(paper_content, paper_id)
            
            if images:
                print("\n💾 Step 7: Saving images to database...")
                images_success = self.image_repository.save_images(images)
                if not images_success:
                    print("⚠️  Warning: Failed to save some images")
                    return False
            else:
                print("⚠️  Warning: No images found or extracted")
            
            # Commit the transaction
            if self.db_connection.connection:
                self.db_connection.connection.commit()
                
            print("\n" + "=" * 60)
            print("🎉 Image processing completed successfully!")
            print(f"   🖼️  Images: {len(images)} images processed")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n✗ Critical error in image processing pipeline: {e}")
            # Rollback on error
            if self.db_connection.connection:
                self.db_connection.connection.rollback()
            return False
            
        finally:
            self.close_connections()
    
    def _check_paper_exists(self, paper_metadata: PaperMetadata) -> Tuple[bool, Dict[str, bool]]:
        """
        Check if paper already exists in database and ask user preference with modular choices.
        
        Args:
            paper_metadata: Paper metadata to check
            
        Returns:
            Tuple of (exists, overwrite_choices_dict)
            where overwrite_choices_dict contains:
            - 'metadata': whether to overwrite paper metadata
            - 'text_sections': whether to overwrite text sections  
            - 'tables': whether to overwrite tables
            - 'images': whether to overwrite images
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
            # Store paper ID for potential updates
            paper_metadata.id = existing_paper['id']
            
            # Get existing data counts for informed decision
            text_sections_count = self.text_sections_repository.count_sections_by_paper_id(existing_paper['id'])
            tables_count = self.table_data_repository.count_tables_by_paper_id(existing_paper['id'])
            images_count = len(self.image_repository.find_by_paper_id(existing_paper['id']))
            
            print(f"\n📊 Existing data:")
            print(f"   Text sections: {text_sections_count}")
            print(f"   Tables: {tables_count}")
            print(f"   Images: {images_count}")
            
            # Ask user what to overwrite with modular choices
            print("\n❓ What would you like to overwrite?")
            print("   1. Skip processing (keep all existing data)")
            print("   2. Overwrite text sections only")
            print("   3. Overwrite tables only") 
            print("   4. Overwrite images only")
            print("   5. Overwrite text sections and tables")
            print("   6. Overwrite text sections and images")
            print("   7. Overwrite tables and images")
            print("   8. Overwrite everything (metadata, text sections, tables, and images)")
            
            while True:
                try:
                    choice = input("Enter choice (1-8): ").strip()
                    
                    if choice == "1":
                        return True, {"metadata": False, "text_sections": False, "tables": False, "images": False}
                    elif choice == "2":
                        return True, {"metadata": False, "text_sections": True, "tables": False, "images": False}
                    elif choice == "3":
                        return True, {"metadata": False, "text_sections": False, "tables": True, "images": False}
                    elif choice == "4":
                        return True, {"metadata": False, "text_sections": False, "tables": False, "images": True}
                    elif choice == "5":
                        return True, {"metadata": False, "text_sections": True, "tables": True, "images": False}
                    elif choice == "6":
                        return True, {"metadata": False, "text_sections": True, "tables": False, "images": True}
                    elif choice == "7":
                        return True, {"metadata": False, "text_sections": False, "tables": True, "images": True}
                    elif choice == "8":
                        return True, {"metadata": True, "text_sections": True, "tables": True, "images": True}
                    else:
                        print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, 7, or 8.")
                        
                except KeyboardInterrupt:
                    print("\n⏭️  Operation cancelled. Skipping paper processing.")
                    return True, {"metadata": False, "text_sections": False, "tables": False, "images": False}
        
        return False, {"metadata": True, "text_sections": True, "tables": True, "images": True}  # doesn't exist, process everything
    
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
    
    def _save_all_tables(self, tables: List[TableData]) -> bool:
        """
        Save all tables to the database.
        
        Args:
            tables: List of TableData objects to save
            
        Returns:
            True if all tables saved successfully, False otherwise
        """
        try:
            success_count = 0
            for table in tables:
                if self.table_data_repository.save_table(table):
                    print(f"✓ Table '{table.title}' saved successfully")
                    success_count += 1
                else:
                    print(f"✗ Failed to save table '{table.title}'")
            
            print(f"✓ Successfully saved {success_count} of {len(tables)} tables")
            return success_count == len(tables)
            
        except Exception as e:
            print(f"✗ Error saving tables: {e}")
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
