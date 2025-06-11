"""
Repository classes for database operations.

This module provides repository pattern implementation for database operations
related to the currently implemented paper metadata functionality.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import psycopg2
from .connection import DatabaseConnection
from ..models import PaperMetadata


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
