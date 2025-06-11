#!/usr/bin/env python3
"""
Utility script to query and display papers stored in the database.
Uses the refactored database system.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from paper_processor import PaperProcessor


def main():
    """Main function."""
    processor = PaperProcessor()
    
    if len(sys.argv) > 1:
        try:
            paper_id = int(sys.argv[1])
            processor.get_paper_details(paper_id)
        except ValueError:
            print("Error: Paper ID must be a number")
            sys.exit(1)
    else:
        processor.list_papers()


if __name__ == "__main__":
    main()
