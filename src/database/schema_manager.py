"""
Database schema management for paper extraction system.

This module provides schema management functionality, refactored from
the existing database/create_tables.py.
"""

from typing import Optional
import psycopg2
from psycopg2 import sql
from .connection import DatabaseConnection


class SchemaManager:
    """
    Manages database schema creation and validation for paper metadata system.
    
    This class encapsulates schema management logic for the currently implemented
    paper_metadata table and schema.
    """
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize schema manager with database connection.
        
        Args:
            db_connection: DatabaseConnection instance
        """
        self.db_connection = db_connection
    
    def check_schema_exists(self, schema_name: str) -> bool:
        """
        Check if a schema exists in the database.
        
        Args:
            schema_name: Name of the schema to check
            
        Returns:
            True if schema exists, False otherwise
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.schemata 
                    WHERE schema_name = %s
                );
            """, (schema_name,))
            result = cursor.fetchone()
            return result[0] if result else False
        finally:
            cursor.close()
    
    def check_table_exists(self, table_name: str, schema_name: str = 'public') -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            schema_name: Name of the schema (default: 'public')
            
        Returns:
            True if table exists, False otherwise
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = %s AND table_name = %s
                );
            """, (schema_name, table_name))
            result = cursor.fetchone()
            return result[0] if result else False
        finally:
            cursor.close()
    
    def create_schema(self, schema_name: str) -> None:
        """
        Create a schema in the database.
        
        Args:
            schema_name: Name of the schema to create
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                sql.Identifier(schema_name)
            ))
            print(f"Schema '{schema_name}' created successfully.")
        finally:
            cursor.close()
    
    def create_paper_metadata_table(self, schema_name: str = 'papers') -> None:
        """
        Create the paper_metadata table for storing extracted paper metadata.
        
        Args:
            schema_name: Name of the schema (default: 'papers')
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.paper_metadata (
                -- Core identification and bibliographic information
                id BIGINT PRIMARY KEY,  -- 64-bit unique identifier
                title TEXT NOT NULL,
                authors TEXT[] DEFAULT ARRAY[]::TEXT[],  -- Array of author names
                journal VARCHAR(500),
                publication_date DATE,
                doi VARCHAR(255),
                volume VARCHAR(50),
                issue VARCHAR(50),
                pages VARCHAR(100),
                abstract TEXT,
                keywords TEXT[] DEFAULT ARRAY[]::TEXT[],  -- Array of keywords
                
                -- Source and extraction metadata
                source_file TEXT NOT NULL,
                extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                
                -- Funding and ethical considerations
                funding_sources TEXT[] DEFAULT ARRAY[]::TEXT[],  -- Array of funding sources
                conflict_of_interest TEXT,
                data_availability TEXT,
                ethics_approval TEXT,
                registration_number VARCHAR(255),
                
                -- Supplemental materials
                supplemental_materials TEXT[] DEFAULT ARRAY[]::TEXT[],  -- Array of supplemental materials
                
                -- Audit fields
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            cursor.execute(create_table_sql)
            print(f"Table '{schema_name}.paper_metadata' created successfully.")
        finally:
            cursor.close()
    
    def create_indexes(self, schema_name: str = 'papers') -> None:
        """
        Create useful indexes for the paper_metadata table.
        
        Args:
            schema_name: Name of the schema (default: 'papers')
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_paper_metadata_title ON {schema_name}.paper_metadata USING GIN(to_tsvector('english', title));",
            f"CREATE INDEX IF NOT EXISTS idx_paper_metadata_authors ON {schema_name}.paper_metadata USING GIN(authors);",
            f"CREATE INDEX IF NOT EXISTS idx_paper_metadata_journal ON {schema_name}.paper_metadata(journal);",
            f"CREATE INDEX IF NOT EXISTS idx_paper_metadata_publication_date ON {schema_name}.paper_metadata(publication_date);",
            f"CREATE INDEX IF NOT EXISTS idx_paper_metadata_doi ON {schema_name}.paper_metadata(doi);",
            f"CREATE INDEX IF NOT EXISTS idx_paper_metadata_keywords ON {schema_name}.paper_metadata USING GIN(keywords);",
            f"CREATE INDEX IF NOT EXISTS idx_paper_metadata_source_file ON {schema_name}.paper_metadata(source_file);",
            f"CREATE INDEX IF NOT EXISTS idx_paper_metadata_extracted_at ON {schema_name}.paper_metadata(extracted_at);",
            f"CREATE INDEX IF NOT EXISTS idx_paper_metadata_abstract ON {schema_name}.paper_metadata USING GIN(to_tsvector('english', abstract));"
        ]
        
        cursor = self.db_connection.connection.cursor()
        try:
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    index_name = index_sql.split('idx_')[1].split(' ')[0]
                    print(f"Index created: {index_name}")
                except Exception as e:
                    print(f"Warning: Could not create index: {e}")
        finally:
            cursor.close()
    
    def create_update_trigger(self, schema_name: str = 'papers') -> None:
        """
        Create a trigger to automatically update the updated_at field.
        
        Args:
            schema_name: Name of the schema (default: 'papers')
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            # Create the trigger function
            trigger_function_sql = """
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            """
            
            cursor.execute(trigger_function_sql)
            print("Trigger function 'update_updated_at_column' created successfully.")
            
            # Create the trigger
            trigger_sql = f"""
            DROP TRIGGER IF EXISTS update_paper_metadata_updated_at ON {schema_name}.paper_metadata;
            CREATE TRIGGER update_paper_metadata_updated_at
                BEFORE UPDATE ON {schema_name}.paper_metadata
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """
            
            cursor.execute(trigger_sql)
            print(f"Trigger 'update_paper_metadata_updated_at' created successfully.")
        finally:
            cursor.close()
    
    def create_text_sections_table(self, schema_name: str = 'papers') -> None:
        """
        Create the text_sections table for storing extracted text sections.
        
        Args:
            schema_name: Name of the schema (default: 'papers')
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.text_sections (
                -- Core identification
                id BIGINT PRIMARY KEY,  -- 64-bit unique identifier
                paper_id BIGINT NOT NULL,  -- Foreign key to paper_metadata
                
                -- Section metadata
                title TEXT NOT NULL,
                section_number INTEGER NOT NULL,
                level INTEGER DEFAULT 1,  -- Heading level (1 for main sections, 2 for subsections, etc.)
                word_count INTEGER DEFAULT 0,
                
                -- Section content and analysis
                content TEXT NOT NULL,  -- Full text content
                summary TEXT NOT NULL,  -- AI-generated summary
                keywords TEXT[] DEFAULT ARRAY[]::TEXT[],  -- AI-generated keywords
                
                -- Audit fields
                extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                
                -- Foreign key constraint
                CONSTRAINT fk_text_sections_paper_id 
                    FOREIGN KEY (paper_id) 
                    REFERENCES {schema_name}.paper_metadata(id) 
                    ON DELETE CASCADE
            );
            """
            
            cursor.execute(create_table_sql)
            print(f"Table '{schema_name}.text_sections' created successfully.")
        finally:
            cursor.close()

    def create_text_sections_indexes(self, schema_name: str = 'papers') -> None:
        """
        Create useful indexes for the text_sections table.
        
        Args:
            schema_name: Name of the schema (default: 'papers')
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_text_sections_paper_id ON {schema_name}.text_sections(paper_id);",
            f"CREATE INDEX IF NOT EXISTS idx_text_sections_title ON {schema_name}.text_sections USING GIN(to_tsvector('english', title));",
            f"CREATE INDEX IF NOT EXISTS idx_text_sections_content ON {schema_name}.text_sections USING GIN(to_tsvector('english', content));",
            f"CREATE INDEX IF NOT EXISTS idx_text_sections_summary ON {schema_name}.text_sections USING GIN(to_tsvector('english', summary));",
            f"CREATE INDEX IF NOT EXISTS idx_text_sections_keywords ON {schema_name}.text_sections USING GIN(keywords);",
            f"CREATE INDEX IF NOT EXISTS idx_text_sections_section_number ON {schema_name}.text_sections(section_number);",
            f"CREATE INDEX IF NOT EXISTS idx_text_sections_level ON {schema_name}.text_sections(level);",
            f"CREATE INDEX IF NOT EXISTS idx_text_sections_extracted_at ON {schema_name}.text_sections(extracted_at);"
        ]
        
        cursor = self.db_connection.connection.cursor()
        try:
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    index_name = index_sql.split('idx_')[1].split(' ')[0]
                    print(f"Index created: {index_name}")
                except Exception as e:
                    print(f"Warning: Could not create index: {e}")
        finally:
            cursor.close()

    def create_text_sections_trigger(self, schema_name: str = 'papers') -> None:
        """
        Create a trigger to automatically update the updated_at field for text_sections.
        
        Args:
            schema_name: Name of the schema (default: 'papers')
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            # Create the trigger for text_sections
            trigger_sql = f"""
            DROP TRIGGER IF EXISTS update_text_sections_updated_at ON {schema_name}.text_sections;
            CREATE TRIGGER update_text_sections_updated_at
                BEFORE UPDATE ON {schema_name}.text_sections
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """
            
            cursor.execute(trigger_sql)
            print(f"Trigger 'update_text_sections_updated_at' created successfully.")
        finally:
            cursor.close()

    def create_table_data_table(self, schema_name: str = 'papers') -> None:
        """
        Create the table_data table for storing extracted tables from papers.
        
        Args:
            schema_name: Name of the schema (default: 'papers')
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.table_data (
                -- Core identification
                id BIGINT PRIMARY KEY,  -- 64-bit unique identifier
                paper_id BIGINT NOT NULL,  -- Foreign key to paper_metadata
                
                -- Table metadata
                table_number INTEGER NOT NULL,
                title TEXT NOT NULL,  -- AI-generated descriptive title
                column_count INTEGER DEFAULT 0,
                row_count INTEGER DEFAULT 0,
                
                -- Table content and analysis
                raw_content TEXT NOT NULL,  -- Raw markdown table content
                summary TEXT NOT NULL,  -- AI-generated comprehensive summary
                context_analysis TEXT NOT NULL,  -- AI analysis of table's research context
                statistical_findings TEXT NOT NULL,  -- AI-identified statistical results
                keywords TEXT[] DEFAULT ARRAY[]::TEXT[],  -- AI-generated keywords
                
                -- Audit fields
                extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                
                -- Foreign key constraint
                CONSTRAINT fk_table_data_paper_id 
                    FOREIGN KEY (paper_id) 
                    REFERENCES {schema_name}.paper_metadata(id) 
                    ON DELETE CASCADE,
                    
                -- Unique constraint to prevent duplicate tables for same paper
                CONSTRAINT uq_table_data_paper_table_number 
                    UNIQUE (paper_id, table_number)
            );
            """
            
            cursor.execute(create_table_sql)
            print(f"Table '{schema_name}.table_data' created successfully.")
        finally:
            cursor.close()

    def create_table_data_indexes(self, schema_name: str = 'papers') -> None:
        """
        Create useful indexes for the table_data table for efficient querying.
        
        Args:
            schema_name: Name of the schema (default: 'papers')
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_table_data_paper_id ON {schema_name}.table_data(paper_id);",
            f"CREATE INDEX IF NOT EXISTS idx_table_data_title ON {schema_name}.table_data USING GIN(to_tsvector('english', title));",
            f"CREATE INDEX IF NOT EXISTS idx_table_data_summary ON {schema_name}.table_data USING GIN(to_tsvector('english', summary));",
            f"CREATE INDEX IF NOT EXISTS idx_table_data_context_analysis ON {schema_name}.table_data USING GIN(to_tsvector('english', context_analysis));",
            f"CREATE INDEX IF NOT EXISTS idx_table_data_statistical_findings ON {schema_name}.table_data USING GIN(to_tsvector('english', statistical_findings));",
            f"CREATE INDEX IF NOT EXISTS idx_table_data_keywords ON {schema_name}.table_data USING GIN(keywords);",
            f"CREATE INDEX IF NOT EXISTS idx_table_data_table_number ON {schema_name}.table_data(table_number);",
            f"CREATE INDEX IF NOT EXISTS idx_table_data_extracted_at ON {schema_name}.table_data(extracted_at);",
            f"CREATE INDEX IF NOT EXISTS idx_table_data_column_count ON {schema_name}.table_data(column_count);",
            f"CREATE INDEX IF NOT EXISTS idx_table_data_row_count ON {schema_name}.table_data(row_count);"
        ]
        
        cursor = self.db_connection.connection.cursor()
        try:
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    index_name = index_sql.split('idx_')[1].split(' ')[0]
                    print(f"Index created: {index_name}")
                except Exception as e:
                    print(f"Warning: Could not create index: {e}")
        finally:
            cursor.close()

    def create_table_data_trigger(self, schema_name: str = 'papers') -> None:
        """
        Create a trigger to automatically update the updated_at timestamp for table_data.
        
        Args:
            schema_name: Name of the schema (default: 'papers')
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            trigger_sql = f"""
            CREATE OR REPLACE TRIGGER update_table_data_updated_at
                BEFORE UPDATE ON {schema_name}.table_data
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
            """
            
            cursor.execute(trigger_sql)
            print(f"Trigger 'update_table_data_updated_at' created successfully.")
        finally:
            cursor.close()

    def create_paper_images_table(self, schema_name: str = 'papers') -> None:
        """
        Create the paper_images table for storing extracted image data and AI analysis.
        
        Args:
            schema_name: Name of the schema (default: 'papers')
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.paper_images (
                -- Core identification
                id BIGINT PRIMARY KEY,  -- 64-bit unique identifier from ImageData
                paper_id BIGINT REFERENCES {schema_name}.paper_metadata(id) ON DELETE CASCADE,
                image_number INTEGER NOT NULL,
                
                -- Image metadata
                alt_text TEXT DEFAULT '',
                image_format VARCHAR(20) DEFAULT '',
                
                -- Image data (base64 encoded)
                image_data TEXT NOT NULL,
                
                -- AI-generated analysis
                summary TEXT NOT NULL,
                graphic_analysis TEXT NOT NULL,
                statistical_analysis TEXT DEFAULT '',
                contextual_relevance TEXT NOT NULL,
                keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
                
                -- Audit fields
                extracted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                
                -- Constraints
                UNIQUE(paper_id, image_number)
            );
            """
            
            cursor.execute(create_table_sql)
            print(f"Table '{schema_name}.paper_images' created successfully.")
        finally:
            cursor.close()

    def create_image_indexes(self, schema_name: str = 'papers') -> None:
        """
        Create useful indexes for the paper_images table.
        
        Args:
            schema_name: Name of the schema (default: 'papers')
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_paper_images_paper_id ON {schema_name}.paper_images(paper_id);",
            f"CREATE INDEX IF NOT EXISTS idx_paper_images_image_number ON {schema_name}.paper_images(image_number);",
            f"CREATE INDEX IF NOT EXISTS idx_paper_images_image_format ON {schema_name}.paper_images(image_format);",
            f"CREATE INDEX IF NOT EXISTS idx_paper_images_keywords ON {schema_name}.paper_images USING GIN(keywords);",
            f"CREATE INDEX IF NOT EXISTS idx_paper_images_summary ON {schema_name}.paper_images USING GIN(to_tsvector('english', summary));",
            f"CREATE INDEX IF NOT EXISTS idx_paper_images_extracted_at ON {schema_name}.paper_images(extracted_at);"
        ]
        
        cursor = self.db_connection.connection.cursor()
        try:
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    index_name = index_sql.split('idx_')[1].split(' ')[0]
                    print(f"Image index created: {index_name}")
                except Exception as e:
                    print(f"Warning: Could not create image index: {e}")
        finally:
            cursor.close()

    def setup_complete_schema(self, schema_name: str = 'papers') -> None:
        """
        Set up the complete database schema for paper metadata.
        
        Args:
            schema_name: Name of the schema to create
        """
        print(f"Setting up complete schema '{schema_name}'...")
        
        # Ensure we have a connection
        if not self.db_connection.connection:
            self.db_connection.connect()
        
        try:
            # Check and create schema if needed
            if not self.check_schema_exists(schema_name):
                print(f"Creating schema '{schema_name}'...")
                self.create_schema(schema_name)
            else:
                print(f"Schema '{schema_name}' already exists.")
            
            # Check and create table if needed
            if not self.check_table_exists('paper_metadata', schema_name):
                print(f"Creating table '{schema_name}.paper_metadata'...")
                self.create_paper_metadata_table(schema_name)
                
                # Create indexes for better performance
                print("Creating indexes...")
                self.create_indexes(schema_name)
                
                # Create update trigger
                print("Creating update trigger...")
                self.create_update_trigger(schema_name)
            else:
                print(f"Table '{schema_name}.paper_metadata' already exists.")
            
            # Check and create text_sections table if needed
            if not self.check_table_exists('text_sections', schema_name):
                print(f"Creating table '{schema_name}.text_sections'...")
                self.create_text_sections_table(schema_name)
                
                # Create indexes for text_sections
                print("Creating indexes for text_sections...")
                self.create_text_sections_indexes(schema_name)
                
                # Create update trigger for text_sections
                print("Creating update trigger for text_sections...")
                self.create_text_sections_trigger(schema_name)
            else:
                print(f"Table '{schema_name}.text_sections' already exists.")
            
            # Check and create table_data table if needed
            if not self.check_table_exists('table_data', schema_name):
                print(f"Creating table '{schema_name}.table_data'...")
                self.create_table_data_table(schema_name)
                
                # Create indexes for table_data
                print("Creating indexes for table_data...")
                self.create_table_data_indexes(schema_name)
                
                # Create update trigger for table_data
                print("Creating update trigger for table_data...")
                self.create_table_data_trigger(schema_name)
            else:
                print(f"Table '{schema_name}.table_data' already exists.")
            
            # Check and create table_data table if needed
            if not self.check_table_exists('table_data', schema_name):
                print(f"Creating table '{schema_name}.table_data'...")
                self.create_table_data_table(schema_name)
                
                # Create indexes for table_data
                print("Creating indexes for table_data...")
                self.create_table_data_indexes(schema_name)
                
                # Create update trigger for table_data
                print("Creating update trigger for table_data...")
                self.create_table_data_trigger(schema_name)
            else:
                print(f"Table '{schema_name}.table_data' already exists.")
            
            # Check and create paper_images table if needed
            if not self.check_table_exists('paper_images', schema_name):
                print(f"Creating table '{schema_name}.paper_images'...")
                self.create_paper_images_table(schema_name)
                
                # Create indexes for paper_images
                print("Creating indexes for paper_images...")
                self.create_image_indexes(schema_name)
            else:
                print(f"Table '{schema_name}.paper_images' already exists.")
            
            # Commit all changes
            if self.db_connection.connection:
                self.db_connection.connection.commit()
            print(f"Schema setup completed successfully for '{schema_name}'!")
            
        except Exception as e:
            print(f"Error setting up schema: {e}")
            if self.db_connection.connection:
                self.db_connection.connection.rollback()
            raise
