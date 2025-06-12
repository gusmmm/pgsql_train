"""
Repository classes for database operations.

This module provides repository pattern implementation for database operations
related to the currently implemented paper metadata functionality.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import psycopg2
import psycopg2.extras
from .connection import DatabaseConnection
from ..models import PaperMetadata, TextSection, TableData


class PaperMetadataRepository:
    """
    Repository for paper metadata database operations.
    
    This class encapsulates all database operations related to paper metadata,
    following the repository pattern for clean separation of concerns.
    """
    
    def __init__(self, db_connection: DatabaseConnection, schema_name: str = 'papers'):
        """
        Initialize the repository.
        
        Args:
            db_connection: DatabaseConnection instance
            schema_name: Name of the schema (default: 'papers')
        """
        self.db_connection = db_connection
        self.schema_name = schema_name
        self.table_name = 'paper_metadata'
    
    def exists_by_doi(self, doi: str) -> bool:
        """
        Check if a paper exists by DOI.
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            True if paper exists, False otherwise
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            cursor.execute(f"""
                SELECT EXISTS(
                    SELECT 1 FROM {self.schema_name}.{self.table_name} 
                    WHERE doi = %s
                )
            """, (doi,))
            result = cursor.fetchone()
            return result[0] if result else False
        finally:
            cursor.close()
    
    def exists_by_title(self, title: str) -> bool:
        """
        Check if a paper exists by exact title match.
        
        Args:
            title: Paper title
            
        Returns:
            True if paper exists, False otherwise
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            cursor.execute(f"""
                SELECT EXISTS(
                    SELECT 1 FROM {self.schema_name}.{self.table_name} 
                    WHERE title = %s
                )
            """, (title,))
            result = cursor.fetchone()
            return result[0] if result else False
        finally:
            cursor.close()
    
    def find_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Find a paper by DOI.
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            Paper data as dictionary or None if not found
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            cursor.execute(f"""
                SELECT id, title, doi FROM {self.schema_name}.{self.table_name} 
                WHERE doi = %s
            """, (doi,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'title': result[1],
                    'doi': result[2]
                }
            return None
        finally:
            cursor.close()
    
    def find_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Find a paper by exact title match.
        
        Args:
            title: Paper title
            
        Returns:
            Paper data as dictionary or None if not found
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            cursor.execute(f"""
                SELECT id, title, doi FROM {self.schema_name}.{self.table_name} 
                WHERE title = %s
            """, (title,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'title': result[1],
                    'doi': result[2] or 'No DOI'
                }
            return None
        finally:
            cursor.close()
    
    def save(self, paper_metadata: PaperMetadata) -> bool:
        """
        Save paper metadata to the database.
        
        Args:
            paper_metadata: PaperMetadata instance to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            # Prepare the INSERT statement
            insert_sql = f"""
                INSERT INTO {self.schema_name}.{self.table_name} (
                    id, title, authors, journal, publication_date, doi, volume, issue, pages, 
                    abstract, keywords, source_file, extracted_at, funding_sources, 
                    conflict_of_interest, data_availability, ethics_approval, 
                    registration_number, supplemental_materials
                ) VALUES (
                    %(id)s, %(title)s, %(authors)s, %(journal)s, %(publication_date)s, %(doi)s, 
                    %(volume)s, %(issue)s, %(pages)s, %(abstract)s, %(keywords)s, %(source_file)s, 
                    %(extracted_at)s, %(funding_sources)s, %(conflict_of_interest)s, 
                    %(data_availability)s, %(ethics_approval)s, %(registration_number)s, 
                    %(supplemental_materials)s
                )
            """
            
            # Parse the extracted_at timestamp if it's a string
            extracted_at = paper_metadata.extracted_at
            if isinstance(extracted_at, str):
                try:
                    # Handle string representation of datetime
                    extracted_at_str = str(extracted_at)
                    extracted_at = datetime.fromisoformat(extracted_at_str.replace('Z', '+00:00'))
                except:
                    extracted_at = datetime.now()
            
            # Parse publication_date if it's a string
            publication_date = paper_metadata.publication_date
            if isinstance(publication_date, str) and publication_date:
                try:
                    # Try to parse various date formats
                    for fmt in ['%Y-%m-%d', '%Y-%m', '%Y', '%d/%m/%Y', '%m/%d/%Y']:
                        try:
                            publication_date = datetime.strptime(publication_date, fmt).date()
                            break
                        except ValueError:
                            continue
                    else:
                        publication_date = None
                except:
                    publication_date = None
            
            # Prepare the data for insertion
            data = {
                'id': paper_metadata.id,
                'title': paper_metadata.title,
                'authors': paper_metadata.authors,
                'journal': paper_metadata.journal,
                'publication_date': publication_date,
                'doi': paper_metadata.doi,
                'volume': paper_metadata.volume,
                'issue': paper_metadata.issue,
                'pages': paper_metadata.pages,
                'abstract': paper_metadata.abstract,
                'keywords': paper_metadata.keywords,
                'source_file': paper_metadata.source_file,
                'extracted_at': extracted_at,
                'funding_sources': paper_metadata.funding_sources,
                'conflict_of_interest': paper_metadata.conflict_of_interest,
                'data_availability': paper_metadata.data_availability,
                'ethics_approval': paper_metadata.ethics_approval,
                'registration_number': paper_metadata.registration_number,
                'supplemental_materials': paper_metadata.supplemental_materials
            }
            
            # Execute the insert
            cursor.execute(insert_sql, data)
            
            print(f"✓ Successfully inserted paper metadata into database.")
            print(f"   Paper ID: {data['id']}")
            print(f"   Title: {data['title']}")
            print(f"   DOI: {data['doi'] or 'No DOI'}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error inserting paper metadata: {e}")
            raise
        finally:
            cursor.close()
    
    def update(self, paper_metadata: PaperMetadata) -> bool:
        """
        Update existing paper metadata in the database.
        
        Args:
            paper_metadata: PaperMetadata instance to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            # Prepare the UPDATE statement
            update_sql = f"""
                UPDATE {self.schema_name}.{self.table_name} SET
                    title = %(title)s,
                    authors = %(authors)s,
                    journal = %(journal)s,
                    publication_date = %(publication_date)s,
                    doi = %(doi)s,
                    volume = %(volume)s,
                    issue = %(issue)s,
                    pages = %(pages)s,
                    abstract = %(abstract)s,
                    keywords = %(keywords)s,
                    source_file = %(source_file)s,
                    extracted_at = %(extracted_at)s,
                    funding_sources = %(funding_sources)s,
                    conflict_of_interest = %(conflict_of_interest)s,
                    data_availability = %(data_availability)s,
                    ethics_approval = %(ethics_approval)s,
                    registration_number = %(registration_number)s,
                    supplemental_materials = %(supplemental_materials)s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %(id)s
            """
            
            # Parse the extracted_at timestamp if it's a string
            extracted_at = paper_metadata.extracted_at
            if isinstance(extracted_at, str):
                try:
                    extracted_at_str = str(extracted_at)
                    extracted_at = datetime.fromisoformat(extracted_at_str.replace('Z', '+00:00'))
                except:
                    extracted_at = datetime.now()
            
            # Parse publication_date if it's a string
            publication_date = paper_metadata.publication_date
            if isinstance(publication_date, str) and publication_date:
                try:
                    for fmt in ['%Y-%m-%d', '%Y-%m', '%Y', '%d/%m/%Y', '%m/%d/%Y']:
                        try:
                            publication_date = datetime.strptime(publication_date, fmt).date()
                            break
                        except ValueError:
                            continue
                    else:
                        publication_date = None
                except:
                    publication_date = None
            
            # Prepare the data for update
            data = {
                'id': paper_metadata.id,
                'title': paper_metadata.title,
                'authors': paper_metadata.authors,
                'journal': paper_metadata.journal,
                'publication_date': publication_date,
                'doi': paper_metadata.doi,
                'volume': paper_metadata.volume,
                'issue': paper_metadata.issue,
                'pages': paper_metadata.pages,
                'abstract': paper_metadata.abstract,
                'keywords': paper_metadata.keywords,
                'source_file': paper_metadata.source_file,
                'extracted_at': extracted_at,
                'funding_sources': paper_metadata.funding_sources,
                'conflict_of_interest': paper_metadata.conflict_of_interest,
                'data_availability': paper_metadata.data_availability,
                'ethics_approval': paper_metadata.ethics_approval,
                'registration_number': paper_metadata.registration_number,
                'supplemental_materials': paper_metadata.supplemental_materials
            }
            
            # Execute the update
            cursor.execute(update_sql, data)
            
            if cursor.rowcount > 0:
                print(f"✓ Paper metadata updated successfully (ID: {paper_metadata.id})")
                return True
            else:
                print(f"✗ No paper found with ID {paper_metadata.id} to update")
                return False
                
        except Exception as e:
            print(f"✗ Error updating paper metadata: {e}")
            return False
        finally:
            cursor.close()

    def find_all(self) -> List[Dict[str, Any]]:
        """
        Find all papers in the database.
        
        Returns:
            List of paper data dictionaries
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            cursor.execute(f"""
                SELECT 
                    id, 
                    title, 
                    authors[1:3] as first_authors,  -- Show first 3 authors
                    journal, 
                    publication_date, 
                    doi,
                    array_length(authors, 1) as total_authors,
                    extracted_at
                FROM {self.schema_name}.{self.table_name} 
                ORDER BY extracted_at DESC
            """)
            
            papers = cursor.fetchall()
            return [
                {
                    'id': paper[0],
                    'title': paper[1],
                    'first_authors': paper[2],
                    'journal': paper[3],
                    'publication_date': paper[4],
                    'doi': paper[5],
                    'total_authors': paper[6],
                    'extracted_at': paper[7]
                }
                for paper in papers
            ]
        finally:
            cursor.close()
    
    def find_by_id(self, paper_id: int) -> Optional[Dict[str, Any]]:
        """
        Find a paper by ID with full details.
        
        Args:
            paper_id: Paper ID
            
        Returns:
            Complete paper data dictionary or None if not found
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            cursor.execute(f"""
                SELECT 
                    id, title, authors, journal, publication_date, doi, volume, issue, pages,
                    abstract, keywords, source_file, extracted_at, funding_sources,
                    conflict_of_interest, data_availability, ethics_approval,
                    registration_number, supplemental_materials, created_at, updated_at
                FROM {self.schema_name}.{self.table_name} 
                WHERE id = %s
            """, (paper_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'title': result[1],
                    'authors': result[2],
                    'journal': result[3],
                    'publication_date': result[4],
                    'doi': result[5],
                    'volume': result[6],
                    'issue': result[7],
                    'pages': result[8],
                    'abstract': result[9],
                    'keywords': result[10],
                    'source_file': result[11],
                    'extracted_at': result[12],
                    'funding_sources': result[13],
                    'conflict_of_interest': result[14],
                    'data_availability': result[15],
                    'ethics_approval': result[16],
                    'registration_number': result[17],
                    'supplemental_materials': result[18],
                    'created_at': result[19],
                    'updated_at': result[20]
                }
            return None
        finally:
            cursor.close()


class TextSectionsRepository:
    """
    Repository for text sections database operations.
    
    This class encapsulates all database operations related to text sections,
    following the repository pattern for clean separation of concerns.
    """
    
    def __init__(self, db_connection: DatabaseConnection, schema_name: str = 'papers'):
        """
        Initialize the repository.
        
        Args:
            db_connection: DatabaseConnection instance
            schema_name: Name of the schema (default: 'papers')
        """
        self.db_connection = db_connection
        self.schema_name = schema_name
        self.table_name = 'text_sections'

    def save(self, text_section: TextSection) -> bool:
        """
        Save a text section to the database.
        
        Args:
            text_section: TextSection instance to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            insert_sql = f"""
                INSERT INTO {self.schema_name}.{self.table_name} (
                    id, paper_id, title, section_number, level, word_count,
                    content, summary, keywords, extracted_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (id) DO UPDATE SET
                    paper_id = EXCLUDED.paper_id,
                    title = EXCLUDED.title,
                    section_number = EXCLUDED.section_number,
                    level = EXCLUDED.level,
                    word_count = EXCLUDED.word_count,
                    content = EXCLUDED.content,
                    summary = EXCLUDED.summary,
                    keywords = EXCLUDED.keywords,
                    extracted_at = EXCLUDED.extracted_at,
                    updated_at = CURRENT_TIMESTAMP;
            """
            
            cursor.execute(insert_sql, (
                text_section.id,
                text_section.paper_id,
                text_section.title,
                text_section.section_number,
                text_section.level,
                text_section.word_count,
                text_section.content,
                text_section.summary,
                text_section.keywords,
                text_section.extracted_at
            ))
            
            print(f"✓ Text section '{text_section.title}' saved successfully")
            return True
            
        except Exception as e:
            print(f"✗ Error saving text section '{text_section.title}': {e}")
            return False
        finally:
            cursor.close()

    def save_all(self, text_sections: List[TextSection]) -> bool:
        """
        Save multiple text sections to the database.
        
        Args:
            text_sections: List of TextSection instances to save
            
        Returns:
            True if all successful, False otherwise
        """
        if not text_sections:
            print("No text sections to save")
            return True
            
        try:
            success_count = 0
            for section in text_sections:
                if self.save(section):
                    success_count += 1
            
            if success_count == len(text_sections):
                print(f"✓ All {len(text_sections)} text sections saved successfully")
                return True
            else:
                print(f"✗ Only {success_count}/{len(text_sections)} text sections saved successfully")
                return False
                
        except Exception as e:
            print(f"✗ Error saving text sections: {e}")
            return False

    def find_by_paper_id(self, paper_id: int) -> List[Dict[str, Any]]:
        """
        Find all text sections for a specific paper.
        
        Args:
            paper_id: Paper ID to search for
            
        Returns:
            List of text section records
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(f"""
                SELECT * FROM {self.schema_name}.{self.table_name}
                WHERE paper_id = %s
                ORDER BY section_number;
            """, (paper_id,))
            
            result = cursor.fetchall()
            return [dict(row) for row in result]
            
        finally:
            cursor.close()

    def exists_by_paper_id(self, paper_id: int) -> bool:
        """
        Check if text sections exist for a specific paper.
        
        Args:
            paper_id: Paper ID to check
            
        Returns:
            True if text sections exist, False otherwise
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            cursor.execute(f"""
                SELECT EXISTS(
                    SELECT 1 FROM {self.schema_name}.{self.table_name}
                    WHERE paper_id = %s
                );
            """, (paper_id,))
            
            result = cursor.fetchone()
            return result[0] if result else False
            
        finally:
            cursor.close()

    def delete_by_paper_id(self, paper_id: int) -> bool:
        """
        Delete all text sections for a specific paper.
        
        Args:
            paper_id: Paper ID to delete sections for
            
        Returns:
            True if successful, False otherwise
        """
        if not self.db_connection.connection:
            raise Exception("No database connection available")
            
        cursor = self.db_connection.connection.cursor()
        try:
            cursor.execute(f"""
                DELETE FROM {self.schema_name}.{self.table_name}
                WHERE paper_id = %s;
            """, (paper_id,))
            
            deleted_count = cursor.rowcount
            print(f"✓ Deleted {deleted_count} text sections for paper ID {paper_id}")
            return True
            
        except Exception as e:
            print(f"✗ Error deleting text sections for paper ID {paper_id}: {e}")
            return False
        finally:
            cursor.close()

    def count_sections_by_paper_id(self, paper_id: int) -> int:
        """
        Count text sections associated with a paper.
        
        Args:
            paper_id: The paper ID to count sections for
            
        Returns:
            Number of text sections for the paper
        """
        if not self.db_connection.connection:
            print("✗ No database connection available")
            return 0
        
        try:
            cursor = self.db_connection.connection.cursor()
            
            count_sql = f"SELECT COUNT(*) FROM {self.schema_name}.{self.table_name} WHERE paper_id = %s"
            cursor.execute(count_sql, (paper_id,))
            result = cursor.fetchone()
            cursor.close()
            
            return result[0] if result else 0
            
        except Exception as e:
            print(f"✗ Error counting text sections: {e}")
            return 0


class TableDataRepository:
    """
    Repository class for table data database operations.
    
    This class follows the project's repository pattern for data access,
    providing a clean interface for table data CRUD operations with proper
    error handling and transaction management.
    """
    
    def __init__(self, db_connection: DatabaseConnection, schema_name: str = 'papers'):
        """
        Initialize the table data repository.
        
        Args:
            db_connection: Database connection instance
            schema_name: Name of the schema containing the table_data table
        """
        self.db_connection = db_connection
        self.schema_name = schema_name
    
    def save_table(self, table_data: 'TableData') -> bool:
        """
        Save a table to the database.
        
        Args:
            table_data: TableData instance to save
            
        Returns:
            Boolean indicating success
        """
        if not self.db_connection.connection:
            print("✗ No database connection available")
            return False
        
        try:
            cursor = self.db_connection.connection.cursor()
            
            insert_sql = f"""
            INSERT INTO {self.schema_name}.table_data (
                id, paper_id, table_number, title, raw_content, 
                summary, context_analysis, statistical_findings, keywords,
                column_count, row_count, extracted_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_sql, (
                table_data.id,
                table_data.paper_id,
                table_data.table_number,
                table_data.title,
                table_data.raw_content,
                table_data.summary,
                table_data.context_analysis,
                table_data.statistical_findings,
                table_data.keywords,
                table_data.column_count,
                table_data.row_count,
                table_data.extracted_at
            ))
            
            cursor.close()
            return True
            
        except Exception as e:
            print(f"✗ Error saving table data: {e}")
            return False
    
    def delete_tables_by_paper_id(self, paper_id: int) -> bool:
        """
        Delete all tables associated with a paper.
        
        Args:
            paper_id: The paper ID whose tables should be deleted
            
        Returns:
            Boolean indicating success
        """
        if not self.db_connection.connection:
            print("✗ No database connection available")
            return False
        
        try:
            cursor = self.db_connection.connection.cursor()
            
            delete_sql = f"DELETE FROM {self.schema_name}.table_data WHERE paper_id = %s"
            cursor.execute(delete_sql, (paper_id,))
            deleted_count = cursor.rowcount
            
            cursor.close()
            
            if deleted_count > 0:
                print(f"✓ Deleted {deleted_count} tables for paper ID {paper_id}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error deleting tables: {e}")
            return False
    
    def count_tables_by_paper_id(self, paper_id: int) -> int:
        """
        Count tables associated with a paper.
        
        Args:
            paper_id: The paper ID to count tables for
            
        Returns:
            Number of tables for the paper
        """
        if not self.db_connection.connection:
            print("✗ No database connection available")
            return 0
        
        try:
            cursor = self.db_connection.connection.cursor()
            
            count_sql = f"SELECT COUNT(*) FROM {self.schema_name}.table_data WHERE paper_id = %s"
            cursor.execute(count_sql, (paper_id,))
            result = cursor.fetchone()
            cursor.close()
            
            return result[0] if result else 0
            
        except Exception as e:
            print(f"✗ Error counting tables: {e}")
            return 0
    
    def find_tables_by_paper_id(self, paper_id: int) -> List['TableData']:
        """
        Find all tables associated with a paper.
        
        Args:
            paper_id: The paper ID to find tables for
            
        Returns:
            List of TableData objects
        """
        if not self.db_connection.connection:
            print("✗ No database connection available")
            return []
        
        try:
            from ..models.table_data import TableData
            
            cursor = self.db_connection.connection.cursor()
            
            select_sql = f"""
            SELECT id, paper_id, table_number, title, raw_content, 
                   summary, context_analysis, statistical_findings, keywords,
                   column_count, row_count, extracted_at
            FROM {self.schema_name}.table_data 
            WHERE paper_id = %s 
            ORDER BY table_number
            """
            
            cursor.execute(select_sql, (paper_id,))
            rows = cursor.fetchall()
            cursor.close()
            
            tables = []
            for row in rows:
                table_data = TableData(
                    id=row[0],
                    paper_id=row[1],
                    table_number=row[2],
                    title=row[3],
                    raw_content=row[4],
                    summary=row[5],
                    context_analysis=row[6],
                    statistical_findings=row[7],
                    keywords=row[8] or [],
                    column_count=row[9],
                    row_count=row[10],
                    extracted_at=row[11]
                )
                tables.append(table_data)
            
            return tables
            
        except Exception as e:
            print(f"✗ Error finding tables: {e}")
            return []
