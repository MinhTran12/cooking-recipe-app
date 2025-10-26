import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'recipe_app'),
    'user': os.getenv('DB_USER', 'recipe_user'),
    'password': os.getenv('DB_PASSWORD', 'recipe_password')
}

@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Context manager for database connections.
    
    Yields:
        psycopg2.extensions.connection: Database connection with auto-commit disabled
    """
    connection = None
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        yield connection
    except psycopg2.Error as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()

@contextmanager
def get_db_cursor() -> Generator[psycopg2.extensions.cursor, None, None]:
    """
    Context manager for database cursors with dictionary-like row access.
    
    Yields:
        psycopg2.extensions.cursor: Database cursor with RealDictCursor factory
    """
    with get_db_connection() as connection:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            connection.commit()
        except psycopg2.Error as e:
            connection.rollback()
            raise e
        finally:
            cursor.close()

def test_database_connection() -> Dict[str, Any]:
    """
    Test the database connection and return status information.
    
    Returns:
        Dict[str, Any]: Connection status and database information
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()['version']
            
            cursor.execute("SELECT COUNT(*) as recipe_count FROM recipes;")
            recipe_count = cursor.fetchone()['recipe_count']
            
            return {
                "status": "connected",
                "database_version": db_version,
                "recipe_count": recipe_count,
                "config": {
                    "host": DB_CONFIG['host'],
                    "port": DB_CONFIG['port'], 
                    "database": DB_CONFIG['database'],
                    "user": DB_CONFIG['user']
                }
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "config": {
                "host": DB_CONFIG['host'],
                "port": DB_CONFIG['port'],
                "database": DB_CONFIG['database'],
                "user": DB_CONFIG['user']
            }
        }