import os
import sqlite3
import psycopg2
from urllib.parse import urlparse
from datetime import datetime

def get_database_connection():
    """Get database connection based on environment"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Production: Use PostgreSQL
        return get_postgres_connection(database_url)
    else:
        # Development: Use SQLite
        return get_sqlite_connection()

def get_postgres_connection(database_url):
    """Get PostgreSQL connection"""
    try:
        # Parse the database URL
        url = urlparse(database_url)
        
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],  # Remove leading slash
            user=url.username,
            password=url.password,
            sslmode='require'
        )
        return conn, 'postgresql'
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        raise

def get_sqlite_connection():
    """Get SQLite connection for development"""
    conn = sqlite3.connect('database.db')
    return conn, 'sqlite'

def execute_query(query, params=None, fetch=False):
    """Execute query with proper database handling"""
    conn, db_type = get_database_connection()
    
    try:
        if db_type == 'postgresql':
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                if 'SELECT' in query.upper():
                    result = cursor.fetchall()
                else:
                    result = cursor.rowcount
            else:
                result = cursor.rowcount
                
            conn.commit()
            return result
        else:
            # SQLite
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
            else:
                result = cursor.rowcount
                
            conn.commit()
            return result
            
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def convert_sqlite_to_postgres_query(sqlite_query):
    """Convert SQLite query to PostgreSQL compatible query"""
    # Replace SQLite specific syntax with PostgreSQL
    postgres_query = sqlite_query.replace('AUTOINCREMENT', 'SERIAL')
    postgres_query = postgres_query.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
    postgres_query = postgres_query.replace('TEXT DEFAULT CURRENT_TIMESTAMP', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    postgres_query = postgres_query.replace('BOOLEAN DEFAULT FALSE', 'BOOLEAN DEFAULT FALSE')
    postgres_query = postgres_query.replace('BOOLEAN DEFAULT TRUE', 'BOOLEAN DEFAULT TRUE')
    
    return postgres_query