"""
Database schema creation module for paper metadata storage.
This module creates the necessary schema and tables to store metadata 
extracted from scientific papers by the paper_agent.py module.
"""
import sys
from pathlib import Path
from .dbmanager import PostgresConnection
from psycopg2 import sql
import psycopg2

def check_schema_exists(cursor, schema_name):
    """
    Check if a schema exists in the database.
    
    Args:
        cursor: Database cursor
        schema_name (str): Name of the schema to check
        
    Returns:
        bool: True if schema exists, False otherwise
    """
    cursor.execute("""
        SELECT EXISTS(
            SELECT 1 FROM information_schema.schemata 
            WHERE schema_name = %s
        );
    """, (schema_name,))
    return cursor.fetchone()[0]

def check_table_exists(cursor, table_name, schema_name='public'):
    """
    Check if a table exists in the database.
    
    Args:
        cursor: Database cursor
        table_name (str): Name of the table to check
        schema_name (str): Name of the schema (default: 'public')
        
    Returns:
        bool: True if table exists, False otherwise
    """
    cursor.execute("""
        SELECT EXISTS(
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        );
    """, (schema_name, table_name))
    return cursor.fetchone()[0]

def create_schema(cursor, schema_name):
    """
    Create a schema in the database.
    
    Args:
        cursor: Database cursor
        schema_name (str): Name of the schema to create
    """
    cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
        sql.Identifier(schema_name)
    ))
    print(f"Schema '{schema_name}' created successfully.")

def create_paper_metadata_table(cursor, schema_name='papers'):
    """
    Create the paper_metadata table to store extracted paper metadata.
    
    Args:
        cursor: Database cursor
        schema_name (str): Name of the schema (default: 'papers')
    """
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

def create_indexes(cursor, schema_name='papers'):
    """
    Create useful indexes for the paper_metadata table.
    
    Args:
        cursor: Database cursor
        schema_name (str): Name of the schema (default: 'papers')
    """
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
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
            print(f"Index created: {index_sql.split('idx_')[1].split(' ')[0]}")
        except Exception as e:
            print(f"Warning: Could not create index: {e}")

def create_update_trigger(cursor, schema_name='papers'):
    """
    Create a trigger to automatically update the updated_at field.
    
    Args:
        cursor: Database cursor
        schema_name (str): Name of the schema (default: 'papers')
    """
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

def setup_database_schema():
    """
    Main function to set up the complete database schema for paper metadata.
    """
    schema_name = 'papers'
    table_name = 'paper_metadata'
    
    print("Starting database schema setup...")
    print("=" * 50)
    
    # Create database connection
    db = PostgresConnection()
    
    try:
        # Connect to the database
        connection = db.connect()
        if not connection:
            raise Exception("Failed to establish database connection")
        cursor = connection.cursor()
        
        # Check if schema exists, create if not
        if check_schema_exists(cursor, schema_name):
            print(f"Schema '{schema_name}' already exists.")
        else:
            print(f"Schema '{schema_name}' does not exist. Creating...")
            create_schema(cursor, schema_name)
        
        # Check if table exists, create if not
        if check_table_exists(cursor, table_name, schema_name):
            print(f"Table '{schema_name}.{table_name}' already exists.")
        else:
            print(f"Table '{schema_name}.{table_name}' does not exist. Creating...")
            create_paper_metadata_table(cursor, schema_name)
            
            # Create indexes for better performance
            print("Creating indexes...")
            create_indexes(cursor, schema_name)
            
            # Create update trigger
            print("Creating update trigger...")
            create_update_trigger(cursor, schema_name)
        
        # Commit all changes
        connection.commit()
        
        # Verify the setup
        print("\nVerifying table structure...")
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema_name, table_name))
        
        columns = cursor.fetchall()
        print(f"\nTable '{schema_name}.{table_name}' columns:")
        print("-" * 80)
        print(f"{'Column Name':<25} {'Data Type':<20} {'Nullable':<10} {'Default'}")
        print("-" * 80)
        for col in columns:
            col_name, data_type, nullable, default = col
            default_str = str(default)[:30] + "..." if default and len(str(default)) > 30 else str(default)
            print(f"{col_name:<25} {data_type:<20} {nullable:<10} {default_str}")
        
        print("\n" + "=" * 50)
        print("Database schema setup completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error setting up database schema: {e}")
        if 'connection' in locals() and connection:
            connection.rollback()
        sys.exit(1)
        
    finally:
        # Close the connection
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    setup_database_schema()