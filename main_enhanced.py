#!/usr/bin/env python3
"""
Enhanced main entry point for the paper processing system.

This script provides a command-line interface with multiple processing options
including full processing, image-only processing, and other selective options.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the processor with absolute imports
from src.paper_processor import PaperProcessor


def show_menu():
    """Display the main menu options."""
    print("\n🚀 Paper Processing System - Enhanced Menu")
    print("=" * 50)
    print("1. Full paper processing (metadata + text + tables + images)")
    print("2. Process images only (requires existing paper in database)")
    print("3. Process text sections only (requires existing paper in database)")
    print("4. Process tables only (requires existing paper in database)")
    print("5. Exit")
    print("=" * 50)


def get_paper_file_path():
    """Get paper file path from user input or command line."""
    # Default paper file path
    default_paper_path = "/home/gusmmm/Desktop/pgsql_train/docs/zanella_2025-with-images.md"
    
    # Check if file path provided as command line argument
    if len(sys.argv) > 1:
        paper_file_path = sys.argv[1]
    else:
        # Ask user for file path
        print(f"\nDefault paper: {default_paper_path}")
        user_path = input("Enter paper file path (or press Enter for default): ").strip()
        paper_file_path = user_path if user_path else default_paper_path
    
    # Validate file exists
    if not os.path.exists(paper_file_path):
        print(f"✗ Error: Paper file does not exist: {paper_file_path}")
        return None
    
    return paper_file_path


def main():
    """Main function with enhanced menu system."""
    print("📄 Enhanced Paper Processing System")
    
    while True:
        try:
            show_menu()
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "5":
                print("👋 Goodbye!")
                sys.exit(0)
            elif choice in ["1", "2", "3", "4"]:
                # Get paper file path
                paper_file_path = get_paper_file_path()
                if not paper_file_path:
                    continue
                
                print(f"📄 Processing paper: {paper_file_path}")
                
                # Create processor
                processor = PaperProcessor()
                success = False
                
                try:
                    if choice == "1":
                        # Full processing
                        print("\n🔄 Starting full paper processing...")
                        success = processor.process_paper(paper_file_path)
                        
                    elif choice == "2":
                        # Images only
                        print("\n🖼️  Starting image-only processing...")
                        success = processor.process_images_only(paper_file_path)
                        
                    elif choice == "3":
                        # Text sections only (would need implementation)
                        print("\n📝 Text-only processing not yet implemented.")
                        print("Please use option 1 (full processing) and select text sections when prompted.")
                        continue
                        
                    elif choice == "4":
                        # Tables only (would need implementation)
                        print("\n📊 Table-only processing not yet implemented.")
                        print("Please use option 1 (full processing) and select tables when prompted.")
                        continue
                    
                    if success:
                        print("\n✅ Processing completed successfully!")
                    else:
                        print("\n❌ Processing failed!")
                        
                except Exception as e:
                    print(f"\n✗ Fatal error: {e}")
                
                # Ask if user wants to continue
                continue_choice = input("\nDo you want to process another paper? (y/N): ").strip().lower()
                if continue_choice not in ['y', 'yes']:
                    print("👋 Goodbye!")
                    break
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled. Goodbye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
