import os
import sys
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'recipe_manager'),
    'user': os.getenv('DB_USER', 'recipe_user'),
    'password': os.getenv('DB_PASSWORD', 'recipe_password')
}

def test_connection() -> bool:
    """Test basic database connection."""
    try:
        print("Testing database connection...")
        
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        
        # Test if recipes table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'recipes'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        # Count recipes
        cursor.execute("SELECT COUNT(*) FROM recipes;")
        recipe_count = cursor.fetchone()[0]
        
        # Display results
        print(f"Successfully connected to PostgreSQL!")
        print(f"Database version: {db_version}")
        print(f"Recipes table exists: {'Yes' if table_exists else 'No'}")
        print(f"Total recipes in database: {recipe_count}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def main():
    """Main test function."""
    print("Recipe Manager - Simple Database Connection Test")
    print("=" * 55)
    
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Connecting to: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print()
    
    # Run connection test
    success = test_connection()
    
    print("\n" + "=" * 55)
    if success:
        print("Database connection test PASSED!")
        print("Your PostgreSQL setup is working correctly.")
    else:
        print("Database connection test FAILED!")
        print("Check if Docker container is running: docker ps")
        print("Check logs: docker-compose logs")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)