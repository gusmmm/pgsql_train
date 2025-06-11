# Paper Processing System - Refactored Architecture

A robust, object-oriented system for extracting metadata from scientific papers using AI and storing them in PostgreSQL with duplicate prevention.

## 🏗️ Architecture Overview

The system has been refactored into a clean, maintainable OOP structure:

```
src/
├── models/                    # Data models
│   ├── paper_metadata.py     # ✅ PaperMetadata model (IMPLEMENTED)
│   └── __init__.py
├── extraction/                # AI extraction components  
│   ├── ai_extractor.py       # ✅ Google Generative AI integration (IMPLEMENTED)
│   └── __init__.py
├── database/                  # Database layer
│   ├── connection.py         # ✅ Database connection management (IMPLEMENTED)
│   ├── schema_manager.py     # ✅ Schema creation/management (IMPLEMENTED)
│   ├── repositories.py       # ✅ Data access layer (IMPLEMENTED)
│   └── __init__.py
├── utils/                     # Utility functions
│   └── __init__.py
└── paper_processor.py        # ✅ Main orchestrator (IMPLEMENTED)

experimental/                  # 🧪 Future enhancements (NOT YET IMPLEMENTED)
├── enhanced_paper_models.py  # Extended models for sections, tables, images
├── enhanced_schema.sql       # Extended database schema  
└── comprehensive_metadata_schema_proposal.md
```

## ✅ Currently Implemented (Paper Metadata)

### Core Features
- **AI-Powered Extraction**: Google Generative AI extracts structured metadata
- **Duplicate Prevention**: Uses DOI and title matching
- **Robust Database Schema**: PostgreSQL with proper indexing
- **Auto-Schema Creation**: Creates database schema if missing
- **OOP Architecture**: Clean, maintainable class structure
- **Error Handling**: Comprehensive error handling and logging

### Data Model
The `PaperMetadata` model captures:
- Core bibliographic information (title, authors, journal, DOI, etc.)
- Publication details (volume, issue, pages, publication date)
- Content (abstract, keywords)
- Funding and ethics information
- Supplemental materials
- Extraction metadata (source file, timestamps)

## 🚀 Quick Start

### Process a Paper
```bash
# Process the default paper
uv run python main.py

# Process a specific paper
uv run python main.py /path/to/paper.md
```

### View Stored Papers
```bash
# List all papers
uv run python list_papers.py

# Get detailed paper info
uv run python list_papers.py <paper_id>
```

## 📊 System Components

### 1. PaperProcessor (Main Orchestrator)
```python
from src.paper_processor import PaperProcessor

processor = PaperProcessor()
success = processor.process_paper("paper.md")
```

**Key Methods:**
- `process_paper(file_path)` - Complete processing pipeline
- `list_papers()` - List all stored papers  
- `get_paper_details(paper_id)` - Get detailed paper information

### 2. AIExtractor (AI Integration)
```python
from src.extraction import AIExtractor

extractor = AIExtractor()
metadata = extractor.extract_metadata(content, file_path)
```

**Features:**
- Google Generative AI integration
- Structured JSON extraction using Pydantic schemas
- Error handling and retry logic

### 3. Database Layer
```python
from src.database import DatabaseConnection, SchemaManager, PaperMetadataRepository

# Connection management
db = DatabaseConnection()
db.connect()

# Schema management  
schema_mgr = SchemaManager(db)
schema_mgr.setup_complete_schema("papers")

# Data access
repo = PaperMetadataRepository(db, "papers")
repo.save_metadata(metadata)
```

### 4. Data Models
```python
from src.models import PaperMetadata

# Generate paper ID
paper_id = PaperMetadata.generate_id(content, file_path)

# Create metadata instance
metadata = PaperMetadata(
    id=paper_id,
    title="Paper Title",
    authors=["Author 1", "Author 2"],
    # ... other fields
)
```

## 🛠️ Configuration

### Environment Variables
```bash
# Google AI API
GOOGLE_API_KEY=your_api_key_here

# PostgreSQL Database
POSTGRES_HOST=localhost
POSTGRES_PORT=8700
POSTGRES_DB=thedb
POSTGRES_USER=theuser
POSTGRES_PASSWORD=thepassword
```

### Database Schema
The system automatically creates:
- Schema: `papers`
- Table: `papers.paper_metadata`
- Indexes: Optimized for DOI, title, and full-text search
- Triggers: Auto-updating timestamps

## 🔄 Processing Pipeline

```
📄 Paper File (.md)
    ↓
📖 FileLoader.load_paper_content()
    ↓  
🤖 AIExtractor.extract_metadata()
    ↓
🏗️ SchemaManager.setup_complete_schema()
    ↓
🔍 PaperMetadataRepository.check_exists()
    ↓
💾 PaperMetadataRepository.save_metadata()
    ↓
✅ Success / ⏭️ Skip if duplicate
```

## 🧪 Future Development (Experimental)

The `experimental/` folder contains designs for future enhancements:

### Planned Features
- **Section Extraction**: Extract hierarchical document sections
- **Table Processing**: Parse and structure tabular data
- **Image Analysis**: Process figures and images
- **Reference Extraction**: Extract and link citations
- **Statistical Data**: Identify and extract statistical information
- **Key Findings**: AI-powered finding extraction

### Extended Data Models
- `Section`, `Table`, `Image`, `Reference` models
- Enhanced schema with relationships
- Statistical data and key findings models

## 🎯 Design Principles

### Current Implementation
1. **Single Responsibility**: Each class has a clear, focused purpose
2. **Dependency Injection**: Components are loosely coupled
3. **Error Handling**: Graceful degradation and detailed logging  
4. **Testability**: Clean interfaces for easy testing
5. **Maintainability**: Clear code structure and documentation

### Database Design
1. **Referential Integrity**: Proper foreign key relationships
2. **Performance**: Optimized indexes for common queries
3. **Scalability**: Designed for large document collections
4. **Flexibility**: Schema supports future extensions

## 📝 Usage Examples

### Basic Paper Processing
```python
from src.paper_processor import PaperProcessor

# Initialize processor
processor = PaperProcessor()

# Process a paper
success = processor.process_paper("research_paper.md")

if success:
    print("Paper processed successfully!")
else:
    print("Processing failed.")
```

### Query Papers
```python
# List all papers
processor.list_papers()

# Get specific paper details  
processor.get_paper_details(7595384199535672686)
```

### Custom Processing
```python
from src.extraction import AIExtractor
from src.database import DatabaseConnection, PaperMetadataRepository

# Custom extraction
extractor = AIExtractor()
metadata = extractor.extract_metadata(content, file_path)

# Custom storage
db = DatabaseConnection()
db.connect()
repo = PaperMetadataRepository(db, "papers")
repo.save_metadata(metadata)
```

## 🔧 Maintenance

### Adding New Fields
1. Update `PaperMetadata` model in `src/models/paper_metadata.py`
2. Update database schema in `src/database/schema_manager.py`
3. Update AI extraction prompts in `src/extraction/ai_extractor.py`

### Performance Tuning
- Monitor query performance using database indexes
- Adjust AI model parameters for extraction quality
- Scale database connections for high throughput

### Error Monitoring
- Check logs for extraction failures
- Monitor database connection issues
- Track duplicate detection accuracy

## 📈 Status Summary

| Component | Status | Description |
|-----------|--------|-------------|
| Paper Metadata | ✅ **IMPLEMENTED** | Core paper information extraction and storage |
| AI Extraction | ✅ **IMPLEMENTED** | Google Generative AI integration |
| Database Layer | ✅ **IMPLEMENTED** | PostgreSQL schema and data access |
| Duplicate Detection | ✅ **IMPLEMENTED** | DOI/title-based duplicate prevention |
| OOP Architecture | ✅ **IMPLEMENTED** | Clean, maintainable class structure |
| Section Extraction | 🧪 **EXPERIMENTAL** | Document section parsing |
| Table Processing | 🧪 **EXPERIMENTAL** | Tabular data extraction |
| Image Analysis | 🧪 **EXPERIMENTAL** | Figure and image processing |
| Statistical Data | 🧪 **EXPERIMENTAL** | Statistical information extraction |

The system is production-ready for paper metadata extraction and provides a solid foundation for future enhancements.
