"""
Database connection management using OOP approach.

This refactors the existing database/dbmanager.py into a cleaner OOP structure.
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv


class DatabaseConnection:
    """
    PostgreSQL database connection manager with environment-based configuration.
    
    This class encapsulates database connection logic with retry mechanism
    and environment variable configuration.
    """
    
    def __init__(
        self, 
        host: Optional[str] = None,
        port: Optional[int] = None,
        dbname: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[int] = None
    ):
        """
        Initialize database connection parameters.
        
        Args:
            host: Database hostname or IP address
            port: Database port number
            dbname: Database name
            user: Database username
            password: Database password
            max_retries: Maximum number of connection retry attempts
            retry_delay: Delay between retry attempts in seconds
        """
        # Load environment variables
        self._load_env_config()
        
        # Set connection parameters (args override env vars)
        self.host = host or os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(port or os.getenv("POSTGRES_PORT", 8700))
        self.dbname = dbname or os.getenv("POSTGRES_DB", "thedb")
        self.user = user or os.getenv("POSTGRES_USER", "theuser")
        self.password = password or os.getenv("POSTGRES_PASSWORD", "thepassword")
        self.max_retries = int(max_retries or os.getenv("POSTGRES_MAX_RETRIES", 5))
        self.retry_delay = int(retry_delay or os.getenv("POSTGRES_RETRY_DELAY", 2))
        
        self.connection: Optional[psycopg2.extensions.connection] = None
    
    def _load_env_config(self) -> None:
        """Load environment variables from .env file."""
        # Find the .env file in the project root directory
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent.parent  # Go up to project root
        env_path = project_root / '.env'
        load_dotenv(dotenv_path=env_path)
    
    def connect(self) -> psycopg2.extensions.connection:
        """
        Connect to the PostgreSQL database with retry mechanism.
        
        Returns:
            Database connection object
            
        Raises:
            Exception: If connection fails after max retry attempts
        """
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                print(f"Attempting to connect to PostgreSQL (Attempt {retry_count + 1}/{self.max_retries})...")
                self.connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password
                )
                print("Connection established successfully!")
                return self.connection
                
            except OperationalError as e:
                retry_count += 1
                if retry_count < self.max_retries:
                    print(f"Connection failed: {e}")
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"Failed to connect after {self.max_retries} attempts.")
                    print(f"Error details: {e}")
                    raise Exception("Database connection failed") from e
        
        # This should never be reached, but added for type safety
        raise Exception("Unexpected error in connection retry loop")
    
    def disconnect(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Database connection closed.")
    
    def test_connection(self) -> bool:
        """
        Test the database connection and display information.
        
        Returns:
            True if connection test is successful, False otherwise
        """
        try:
            # Ensure we have a connection
            if not self.connection:
                self.connect()
                
            # Ensure connection is not None
            if not self.connection:
                print("Failed to establish connection")
                return False
                
            # Create a cursor
            cursor = self.connection.cursor()
            
            # Get PostgreSQL version
            cursor.execute("SELECT version();")
            version_result = cursor.fetchone()
            version = version_result[0] if version_result else "Unknown"
            
            # Get current database name
            cursor.execute("SELECT current_database();")
            db_result = cursor.fetchone()
            current_db = db_result[0] if db_result else "Unknown"
            
            # Get current user
            cursor.execute("SELECT current_user;")
            user_result = cursor.fetchone()
            current_user = user_result[0] if user_result else "Unknown"
            
            # Get database size
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database())) 
                AS database_size;
            """)
            size_result = cursor.fetchone()
            db_size = size_result[0] if size_result else "Unknown"
            
            # Print information
            print("\n" + "="*50)
            print("DATABASE CONNECTION INFORMATION")
            print("="*50)
            print(f"PostgreSQL Version: {version}")
            print(f"Connected Database: {current_db}")
            print(f"Connected User: {current_user}")
            print(f"Database Size: {db_size}")
            print(f"Connection Parameters:")
            print(f"  - Host: {self.host}")
            print(f"  - Port: {self.port}")
            print(f"  - Database: {self.dbname}")
            print(f"  - User: {self.user}")
            print("="*50 + "\n")
            
            # Close the cursor
            cursor.close()
            
            return True
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
