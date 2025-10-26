import json
import os
import sys
import uuid
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'recipe_manager'),
    'user': os.getenv('DB_USER', 'recipe_user'),
    'password': os.getenv('DB_PASSWORD', 'recipe_password')
}

def load_mock_recipes():
    """Load mock recipes from JSON file."""
    script_dir = Path(__file__).parent
    json_file = script_dir / 'mockRecipes.json'
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        print(f"Loaded {len(recipes)} recipes from {json_file}")
        return recipes
    except FileNotFoundError:
        print(f"Could not find {json_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {json_file}: {e}")
        return None

def clear_existing_recipes(cursor):
    """Clear existing recipes from database."""
    try:
        cursor.execute("DELETE FROM recipes;")
        print("Cleared existing recipes from database")
        return True
    except Exception as e:
        print(f"Failed to clear existing recipes: {e}")
        return False

def seed_recipes(recipes):
    """Seed the database with mock recipe data."""
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Clear existing data
        if not clear_existing_recipes(cursor):
            return False
        
        # Insert each recipe
        inserted_count = 0
        for recipe in recipes:
            try:
                # Generate a new UUID for each recipe
                recipe_id = str(uuid.uuid4())
                
                # Map JSON field names to database field names
                insert_query = """
                    INSERT INTO recipes (
                        id, title, image, ingredients, instructions, 
                        time_to_prepare, tags, calories_per_serving, 
                        serving_size, favorite
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                
                cursor.execute(insert_query, (
                    recipe_id,
                    recipe['title'],
                    recipe['image'],
                    recipe['ingredients'],
                    recipe['instructions'],
                    recipe['timeToPrepare'],
                    recipe['tags'],
                    recipe['caloriesPerServing'],
                    recipe['servingSize'],
                    recipe['favorite']
                ))
                
                inserted_count += 1
                print(f"Inserted: {recipe['title']} (ID: {recipe_id})")
                
            except Exception as e:
                print(f"Failed to insert {recipe.get('title', 'Unknown')}: {e}")
                continue
        
        # Commit all changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\nSuccessfully seeded {inserted_count}/{len(recipes)} recipes!")
        return True
        
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def verify_seeding():
    """Verify that the seeding was successful."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Count total recipes
        cursor.execute("SELECT COUNT(*) as count FROM recipes;")
        total_count = cursor.fetchone()['count']
        
        # Count favorites
        cursor.execute("SELECT COUNT(*) as count FROM recipes WHERE favorite = true;")
        favorite_count = cursor.fetchone()['count']
        
        # Get sample recipe
        cursor.execute("SELECT title, time_to_prepare, array_length(tags, 1) as tag_count FROM recipes LIMIT 1;")
        sample = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print("\nVerification Results:")
        print(f"   • Total recipes: {total_count}")
        print(f"   • Favorite recipes: {favorite_count}")
        if sample:
            print(f"   • Sample recipe: {sample['title']} ({sample['time_to_prepare']} min, {sample['tag_count']} tags)")
        
        return True
        
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

def main():
    """Main seeder function."""
    print("Recipe Database Seeder")
    print("=" * 40)
    
    recipes = load_mock_recipes()
    if not recipes:
        return 1
    
    if not seed_recipes(recipes):
        return 1

    if not verify_seeding():
        print("Warning: Could not verify seeding results")
    
    print("\nDatabase seeding completed successfully!")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)