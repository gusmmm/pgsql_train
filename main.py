#!/usr/bin/env python
"""
Main script for PostgreSQL connection demo.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from database import PostgresConnection

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)

def main():
    """
    Main function to demonstrate PostgreSQL connection.
    """
    # Create a PostgreSQL connection object using environment variables from .env file
    # Environment variables used:
    # - POSTGRES_HOST: Database hostname or IP address
    # - POSTGRES_PORT: Database port number
    # - POSTGRES_DB: Database name
    # - POSTGRES_USER: Database username
    # - POSTGRES_PASSWORD: Database password
    # - POSTGRES_MAX_RETRIES: Maximum connection retry attempts
    # - POSTGRES_RETRY_DELAY: Delay between retry attempts in seconds
    db = PostgresConnection()
    
    try:
        # Connect to the database
        db.connect()
        
        # Test the connection and display information
        db.test_connection()
        
        print("Connection to PostgreSQL was successful!")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        # Close the connection if it exists
        if db.connection:
            db.connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    sys.exit(main())
