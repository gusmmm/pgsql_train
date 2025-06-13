\
from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from the project root .env file
# Assuming this script is in /frontend/api/main.py, root is three levels up
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if not os.path.exists(dotenv_path):
    print(f"Warning: .env file not found at {dotenv_path}. Database credentials might be missing.")
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT", "5432") # Default port if not specified
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None
    except Exception as e: # Catch other potential errors
        print(f"An unexpected error occurred during DB connection: {e}")
        return None

@app.route('/api/db/status', methods=['GET'])
def db_status():
    conn = get_db_connection()
    if conn:
        try:
            conn.close()
            return jsonify({"status": "online", "host": os.getenv("POSTGRES_HOST"), "port": os.getenv("POSTGRES_PORT"), "name": os.getenv("POSTGRES_DB")})
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error closing connection: {str(e)}"}), 500
    else:
        return jsonify({"status": "offline", "error": "Failed to connect to the database"}), 500

@app.route('/api/db/schemas', methods=['GET'])
def get_schemas():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    schemas_list = []
    try:
        cursor = conn.cursor()
        # Query to get user-defined schemas
        cursor.execute('''
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            AND schema_name NOT LIKE 'pg_temp_%' 
            AND schema_name NOT LIKE 'pg_toast_temp_%';
        ''')
        schemas_list = [row[0] for row in cursor.fetchall()]
        cursor.close()
    except psycopg2.Error as e:
        return jsonify({"error": f"Database query failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
    return jsonify({"schemas": schemas_list})

@app.route('/api/db/schema/<schema_name>/details', methods=['GET'])
def get_schema_details(schema_name):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    details = {"schemaName": schema_name, "tables": [], "views": [], "functions": []}
    
    try:
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_type = 'BASE TABLE';
        ''', (schema_name,))
        details["tables"] = [row[0] for row in cursor.fetchall()]
        
        # Get views
        cursor.execute('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_type = 'VIEW';
        ''', (schema_name,))
        details["views"] = [row[0] for row in cursor.fetchall()]
        
        # Get functions
        cursor.execute('''
            SELECT routine_name
            FROM information_schema.routines
            WHERE specific_schema = %s;
        ''', (schema_name,))
        # Use set to get unique function names as routines can list overloaded functions
        details["functions"] = sorted(list(set(row[0] for row in cursor.fetchall())))
        
        cursor.close()
    except psycopg2.Error as e:
        return jsonify({"error": f"Database query failed for schema {schema_name}: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred for schema {schema_name}: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()
            
    return jsonify(details)

if __name__ == '__main__':
    # Make sure .env is loaded
    if not (os.getenv("POSTGRES_HOST") and os.getenv("POSTGRES_USER") and os.getenv("POSTGRES_DB")):
        print("CRITICAL: Database environment variables (POSTGRES_HOST, POSTGRES_USER, POSTGRES_DB) not set.")
        print(f"Attempted to load .env from: {dotenv_path}")
        print("Please ensure a .env file exists in the project root or that these variables are set in your environment.")
    app.run(debug=True, port=5001)
