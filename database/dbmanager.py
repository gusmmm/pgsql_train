"""
Database connection module for PostgreSQL training project.
This module provides functionality to connect to the PostgreSQL database 
with credentials loaded from the .env file.
"""
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError

# Load environment variables from .env file
# Find the .env file in the project root directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class PostgresConnection:
    """PostgreSQL database connection handler."""
    
    def __init__(self, host=None, port=None, dbname=None, 
                 user=None, password=None, max_retries=None, retry_delay=None):
        """
        Initialize database connection parameters from environment variables.
        If parameters are provided directly, they override environment variables.
        
        Args:
            host (str, optional): Database hostname or IP address
            port (int, optional): Database port number
            dbname (str, optional): Database name
            user (str, optional): Database username
            password (str, optional): Database password
            max_retries (int, optional): Maximum number of connection retry attempts
            retry_delay (int, optional): Delay between retry attempts in seconds
        """
        # Get settings from environment variables with fallbacks to default values
        self.host = host or os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(port or os.getenv("POSTGRES_PORT", 8700))
        self.dbname = dbname or os.getenv("POSTGRES_DB", "thedb")
        self.user = user or os.getenv("POSTGRES_USER", "theuser")
        self.password = password or os.getenv("POSTGRES_PASSWORD", "thepassword")
        self.max_retries = int(max_retries or os.getenv("POSTGRES_MAX_RETRIES", 5))
        self.retry_delay = int(retry_delay or os.getenv("POSTGRES_RETRY_DELAY", 2))
        self.connection = None
        
    def connect(self):
        """
        Connect to the PostgreSQL database.
        
        Returns:
            psycopg2.extensions.connection: Database connection object if successful
            
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
    
    def test_connection(self):
        """
        Test the database connection and print relevant information.
        
        Returns:
            bool: True if connection test is successful, False otherwise
        """
        try:
            # Ensure we have a connection
            if not self.connection:
                self.connect()
                
            # Create a cursor
            cursor = self.connection.cursor()
            
            # Get PostgreSQL version
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            # Get current database name
            cursor.execute("SELECT current_database();")
            current_db = cursor.fetchone()[0]
            
            # Get current user
            cursor.execute("SELECT current_user;")
            current_user = cursor.fetchone()[0]
            
            # Get database size
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database())) 
                AS database_size;
            """)
            db_size = cursor.fetchone()[0]
            
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
        
        
# Example usage
if __name__ == "__main__":
    # Create an instance of PostgresConnection using environment variables
    print("Creating PostgreSQL connection using environment variables from .env file...")
    db = PostgresConnection()
    
    try:
        # Test the connection
        if db.test_connection():
            print("Connection test successful!")
        else:
            print("Connection test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        # Close the connection if it exists
        if db.connection:
            db.connection.close()
            print("Database connection closed.")
