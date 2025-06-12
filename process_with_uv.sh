#!/bin/bash
# Script to run paper processing with uv
# Usage: ./process_with_uv.sh [paper_file]

set -e

# Default paper file if none provided
PAPER_FILE="${1:-docs/zanella_2025-with-images.md}"

echo "🚀 Running paper processor with uv..."
echo "📄 Processing file: $PAPER_FILE"
echo "==============================================="

# Run with uv
exec uv run python main.py "$PAPER_FILE"
