# Paper Processing System

A robust system for extracting metadata from scientific papers using AI and storing them in PostgreSQL with duplicate prevention.

## Features

✅ **AI-Powered Extraction**: Uses Google Generative AI to extract structured metadata from papers  
✅ **Duplicate Prevention**: Uses DOI and title matching to prevent duplicate entries  
✅ **Robust Database Schema**: PostgreSQL schema with proper indexing and constraints  
✅ **Automatic Schema Creation**: Creates database schema if it doesn't exist  
✅ **Comprehensive Metadata**: Extracts 20+ fields including authors, abstract, funding, ethics info  
✅ **Error Handling**: Graceful error handling and detailed logging  
✅ **Maintenance Utilities**: Scripts to query and manage stored papers  

## System Architecture

```
📄 Paper (MD file) 
    ↓
🤖 AI Extraction (Google Generative AI)
    ↓  
🔍 Duplicate Check (DOI/Title)
    ↓
💾 PostgreSQL Storage (papers.paper_metadata)
```

## Quick Start

### 1. Setup Environment
Ensure your `.env` file has:
```bash
GOOGLE_API_KEY=your_google_api_key_here
POSTGRES_HOST=localhost
POSTGRES_PORT=8700
POSTGRES_DB=thedb
POSTGRES_USER=theuser
POSTGRES_PASSWORD=thepassword
```

### 2. Process a Paper
```bash
# Process the default paper
uv run python process_paper.py

# Process a specific paper file
uv run python process_paper.py /path/to/your/paper.md
```

### 3. View Stored Papers
```bash
# List all papers
uv run python list_papers.py

# Get detailed view of specific paper
uv run python list_papers.py <paper_id>
```

## Scripts Overview

### Core Scripts

- **`process_paper.py`** - Main processing pipeline
  - Loads paper content
  - Extracts metadata using AI
  - Checks for duplicates
  - Creates schema if needed
  - Stores in database

- **`list_papers.py`** - Query utility
  - Lists all papers with summary info
  - Shows detailed paper information

### Supporting Modules

- **`database/create_tables.py`** - Database schema management
- **`database/dbmanager.py`** - Database connection handling
- **`experimental/paper_agent.py`** - AI extraction components

## Database Schema

The system creates a PostgreSQL schema called `papers` with the main table `paper_metadata`:

### Key Fields
- **`id`**: 64-bit unique identifier (generated)
- **`title`**: Paper title
- **`authors`**: Array of author names
- **`doi`**: Digital Object Identifier (used for duplicate detection)
- **`journal`**, **`publication_date`**, **`volume`**, **`issue`**, **`pages`**
- **`abstract`**: Full abstract text
- **`keywords`**: Array of keywords
- **`funding_sources`**: Array of funding sources
- **`conflict_of_interest`**, **`data_availability`**, **`ethics_approval`**
- **`supplemental_materials`**: Array of supplemental materials
- **`source_file`**: Path to original paper file
- **`extracted_at`**: AI extraction timestamp
- **`created_at`**, **`updated_at`**: Database audit fields

### Indexes
- Full-text search on title and abstract
- GIN indexes on array fields (authors, keywords)
- Standard indexes on DOI, journal, dates

## Duplicate Prevention Logic

1. **Primary Check**: DOI matching (most reliable)
2. **Fallback Check**: Exact title matching
3. **Action**: Skip insertion if duplicate found, display existing paper info

## Error Handling

The system handles various error conditions gracefully:
- Missing Google API key
- File not found
- Database connection issues
- AI extraction failures
- Invalid JSON responses
- Database schema issues

## Example Output

```
🚀 Starting paper processing pipeline...
============================================================

📖 Step 1: Loading paper content...
✓ Successfully loaded paper content from: /path/to/paper.md

🤖 Step 2: Extracting metadata using AI...
✓ Generated 64-bit ID: 7595384199535672686
✓ Google GenAI client initialized successfully.
✓ Successfully extracted and parsed metadata.

🗄️  Step 3: Setting up database connection...
✓ Database connection established.

📋 Step 4: Ensuring database schema exists...
✓ Schema 'papers' already exists.
✓ Table 'papers.paper_metadata' already exists.

🔍 Step 5: Checking for duplicate papers...

💾 Step 6: Inserting paper metadata...
✓ Successfully inserted paper metadata into database.
   Paper ID: 7595384199535672686
   Title: Dwell Time and Risk of Bloodstream Infection...
   DOI: 10.1001/jamanetworkopen.2025.7202

============================================================
🎉 Paper processing completed successfully!
============================================================
```

## Maintenance

- **Schema Updates**: Modify `database/create_tables.py` for schema changes
- **AI Prompts**: Adjust prompts in `process_paper.py` for better extraction
- **Duplicate Logic**: Customize duplicate detection in `check_paper_exists()`
- **Database Queries**: Use `list_papers.py` as template for custom queries

## Requirements

- Python 3.8+
- PostgreSQL database
- Google Generative AI API key
- Required Python packages (managed by `uv`)

## Usage Tips

1. **Batch Processing**: Process multiple papers by running the script in a loop
2. **Monitoring**: Check logs for extraction quality and adjust AI prompts as needed
3. **Backup**: Regular database backups recommended for production use
4. **Performance**: Indexes are optimized for common queries (DOI, title, date ranges)
