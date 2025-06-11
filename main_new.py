#!/usr/bin/env python3
"""
Main entry point for the paper processing system.

This script provides a command-line interface to the refactored
paper processing pipeline.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from paper_processor import PaperProcessor


def main():
    """Main function to run the paper processor."""
    # Default paper file path
    default_paper_path = "/home/gusmmm/Desktop/pgsql_train/docs/zanella_2025-with-images.md"
    
    # Get paper file path from command line argument or use default
    if len(sys.argv) > 1:
        paper_file_path = sys.argv[1]
    else:
        paper_file_path = default_paper_path
    
    # Check if file exists
    if not os.path.exists(paper_file_path):
        print(f"✗ Error: Paper file does not exist: {paper_file_path}")
        sys.exit(1)
    
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
