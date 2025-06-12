# GitHub Copilot Instructions for Paper Processing System

## Project Overview

This is a **robust, OOP-based scientific paper metadata extraction and storage system** that uses AI (Google Generative AI) and PostgreSQL. The system is designed to be modular, maintainable, and extensible, following strict architectural principles.

## 🏗️ Architecture Principles

### 1. **Modular Design & Separation of Concerns**
- Each module has a single, well-defined responsibility
- Clear separation between data models, extraction logic, database operations, and orchestration
- Dependencies flow inward: database ← extraction ← models ← utils

### 2. **Object-Oriented Programming (OOP)**
- All major components are implemented as classes with clear interfaces
- Use composition over inheritance
- Encapsulate data and behavior together
- Follow SOLID principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion)

### 3. **Dependency Injection**
- Components receive their dependencies through constructors or method parameters
- No hardcoded dependencies or global state
- Easy to test and mock components

### 4. **Robust Error Handling**
- Comprehensive try-catch blocks with specific error messages
- Graceful degradation when possible
- Clear logging and user feedback
- Return boolean success indicators for operations

### 5. **Data Validation & Type Safety**
- Use Pydantic models for all data structures
- Strong typing with Python type hints
- Validate data at system boundaries

### 6. **Using python**
- Follow PEP 8 style guide for Python code
- Use clear, descriptive names for classes, methods, and variables
- Write docstrings for all classes and methods
- Use type hints for function signatures
- Use uv for project management and virtual environments instead of pip

## 📁 Project Structure

```
pgsql_train/
├── 🚀 Entry Points (PRODUCTION READY)
│   ├── main.py                          # ✅ Main paper processor entry point
│   └── list_papers.py                   # ✅ Query/list papers utility
│
├── 🏗️ Core System (PRODUCTION READY)
│   └── src/
│       ├── models/
│       │   ├── paper_metadata.py        # ✅ PaperMetadata Pydantic model
│       │   └── __init__.py
│       ├── extraction/
│       │   ├── ai_extractor.py         # ✅ Google AI integration 
│       │   └── __init__.py
│       ├── database/
│       │   ├── connection.py           # ✅ Database connection management
│       │   ├── schema_manager.py       # ✅ Schema creation/management
│       │   ├── repositories.py         # ✅ Data access layer
│       │   └── __init__.py
│       ├── utils/
│       │   └── __init__.py
│       └── paper_processor.py          # ✅ Main orchestrator class
│
├── 🧪 Future Development (EXPERIMENTAL)
│   └── experimental/
│       ├── enhanced_paper_models.py    # 🧪 Extended models (sections, tables, images)
│       ├── enhanced_schema.sql         # 🧪 Extended database schema
│       └── comprehensive_metadata_schema_proposal.md
│
└── 🗃️ Legacy (DEPRECATED - DO NOT EXTEND)
    └── database/
        └── dbmanager.py                # 🔄 Legacy - superseded by src/database/
```

## 🎯 What's Ready for Production

### ✅ Implemented & Tested (Paper Metadata)
- **Complete Pipeline**: File → AI Extraction → Database Storage
- **OOP Architecture**: Clean, maintainable class structure
- **AI Integration**: Google Generative AI for metadata extraction
- **Database Layer**: PostgreSQL with schema management
- **Duplicate Detection**: DOI/title-based prevention
- **Error Handling**: Comprehensive error management
- **Entry Points**: Simple command-line interface

### 🧪 Experimental (NOT YET IMPLEMENTED)
- Section extraction and hierarchy
- Table parsing and structure analysis  
- Image and figure processing
- Reference and citation extraction
- Statistical data identification
- Key findings extraction

## 📝 Coding Style Guidelines

### Python Code Style
```python
# Class naming: PascalCase
class PaperProcessor:
    """Main orchestrator for paper processing."""
    
    def __init__(self, schema_name: str = 'papers'):
        """Initialize with dependency injection."""
        self.schema_name = schema_name
        self.db_connection = DatabaseConnection()
        self.extractor = AIExtractor()
    
    def process_paper(self, file_path: str) -> bool:
        """Process paper with clear return value."""
        try:
            # Implementation with comprehensive error handling
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
```

### Database Patterns
```python
# Repository pattern for data access
class PaperMetadataRepository:
    """Data access layer for paper metadata."""
    
    def __init__(self, db_connection: DatabaseConnection, schema_name: str):
        self.db_connection = db_connection
        self.schema_name = schema_name
    
    def save_paper(self, paper: PaperMetadata) -> bool:
        """Save paper with transaction safety."""
        try:
            with self.db_connection.get_connection() as conn:
                # Implementation
                return True
        except Exception as e:
            print(f"✗ Database error: {e}")
            return False
```

### Error Handling Pattern
```python
def example_operation(self) -> bool:
    """Always return boolean success indicators."""
    try:
        # Main operation logic
        print("✓ Operation successful")
        return True
    except SpecificError as e:
        print(f"✗ Specific error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
```

## 🔧 Development Guidelines

### When Adding New Features

1. **Start in `/experimental/`**
   - Implement new features in the experimental directory first
   - Test thoroughly and validate the approach
   - Follow the same OOP and modular design patterns

2. **Migration to Production**
   - Once tested, migrate working code to `/src/`
   - Follow existing patterns and structure
   - Update entry points as needed
   - Remove experimental code only after production migration

3. **Code Review Checklist**
   - [ ] Follows OOP principles
   - [ ] Uses dependency injection
   - [ ] Has comprehensive error handling
   - [ ] Returns clear success/failure indicators
   - [ ] Includes proper type hints
   - [ ] Uses Pydantic for data validation
   - [ ] Has appropriate logging/user feedback

### Database Schema Changes

1. **Test in `/experimental/enhanced_schema.sql`** first
2. **Ensure backward compatibility** with existing production schema
3. **Update schema manager** in `/src/database/schema_manager.py`
4. **Add repository methods** for new data access patterns

### AI Integration Patterns

```python
# Always use the established AIExtractor pattern
class NewExtractor:
    """Follow the established pattern."""
    
    def __init__(self):
        self.client = self._initialize_client()
    
    def extract_data(self, content: str) -> Optional[DataModel]:
        """Use Pydantic models for structured output."""
        try:
            # Implementation
            return structured_data
        except Exception as e:
            print(f"✗ Extraction error: {e}")
            return None
```

## 🚫 What NOT to Do

### ❌ Anti-Patterns
- **No monolithic scripts** - Everything must be modular and class-based
- **No hardcoded dependencies** - Use dependency injection
- **No global state** - Pass dependencies explicitly
- **No mixed concerns** - Keep extraction, database, and orchestration separate
- **No silent failures** - Always provide clear error messages and return codes
- **No direct database queries in business logic** - Use repository pattern

### ❌ Don't Extend Legacy Code
- Don't modify `/database/dbmanager.py` - use `/src/database/` instead
- Don't create new monolithic scripts in the root directory
- Don't bypass the established OOP structure

## 🔄 Migration Strategy for Future Features

When implementing features from `/experimental/`:

1. **Phase 1**: Choose one feature (e.g., section extraction)
2. **Phase 2**: Implement in `/experimental/` following OOP patterns
3. **Phase 3**: Test thoroughly with sample papers
4. **Phase 4**: Migrate working code to `/src/` following established structure
5. **Phase 5**: Update orchestrator (`paper_processor.py`) to use new feature
6. **Phase 6**: Update entry points if needed
7. **Phase 7**: Remove experimental code once production is stable

## 🧪 Current Experimental Features

The following features are designed but not yet implemented:
- **Enhanced Section Model**: Hierarchical sections with metadata
- **Table Extraction**: Structure analysis and data parsing
- **Image Processing**: Figure classification and metadata
- **Reference Parsing**: Citation extraction and linking
- **Statistical Data**: P-values, confidence intervals, etc.
- **Key Findings**: Automated identification of research outcomes

## 🎯 Success Metrics

When implementing new features, ensure:
- [ ] **Maintainability**: Code is easy to understand and modify
- [ ] **Testability**: Components can be easily unit tested
- [ ] **Extensibility**: New features can be added without breaking existing code
- [ ] **Reliability**: Robust error handling and graceful degradation
- [ ] **Performance**: Efficient database operations and AI calls
- [ ] **Documentation**: Clear docstrings and comments

## 🔍 Examples of Good Patterns

### Data Flow
```
File Input → AIExtractor → PaperMetadata → Repository → Database
     ↓
PaperProcessor (orchestrates the flow)
     ↓
Clear success/failure feedback to user
```

### Class Interaction
```python
# Good: Dependency injection and clear interfaces
processor = PaperProcessor(schema_name='papers')
success = processor.process_paper('/path/to/paper.md')

# Good: Repository pattern
repository = PaperMetadataRepository(db_connection, 'papers')
paper = repository.find_by_doi('10.1000/example')
```

## 🎓 Learning Resources

For contributors new to the project:
1. Study `/src/paper_processor.py` to understand the orchestration pattern
2. Review `/src/models/paper_metadata.py` for data modeling approach
3. Examine `/src/database/repositories.py` for database patterns
4. Look at `/experimental/` for examples of future feature design

Remember: **Consistency is key**. Follow established patterns and principles to maintain the system's integrity and maintainability.
