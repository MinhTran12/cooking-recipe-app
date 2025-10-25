import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from main import app
from database import get_db_cursor


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def sample_recipe_data():
    """Sample recipe data for testing."""
    return {
        "title": "Test Chocolate Cake",
        "image": "/test/images/cake.jpg",
        "ingredients": ["flour", "cocoa powder", "sugar", "eggs", "butter"],
        "instructions": ["Mix dry ingredients", "Add wet ingredients", "Bake for 30 minutes"],
        "time_to_prepare": 45,
        "tags": ["dessert", "chocolate", "cake"],
        "calories_per_serving": 350,
        "serving_size": 8,
        "favorite": False
    }


@pytest.fixture
def updated_recipe_data():
    """Sample recipe update data for testing."""
    return {
        "title": "Updated Chocolate Cake",
        "time_to_prepare": 50,
        "favorite": True
    }


@pytest.fixture(scope="function")
def clean_test_recipe():
    """Fixture that creates a test recipe and cleans it up after the test."""
    recipe_id = None
    
    def _create_test_recipe(recipe_data):
        nonlocal recipe_id
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO recipes (
                    id, title, image, ingredients, instructions, time_to_prepare, 
                    tags, calories_per_serving, serving_size, favorite, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id;
            """, (
                recipe_data["title"],
                recipe_data.get("image"),
                recipe_data["ingredients"],
                recipe_data["instructions"],
                recipe_data["time_to_prepare"],
                recipe_data["tags"],
                recipe_data["calories_per_serving"],
                recipe_data["serving_size"],
                recipe_data.get("favorite", False),
                datetime.now(),
                datetime.now()
            ))
            recipe_id = cursor.fetchone()["id"]
        return recipe_id
    
    yield _create_test_recipe
    
    # Cleanup after test
    if recipe_id:
        try:
            with get_db_cursor() as cursor:
                cursor.execute("DELETE FROM recipes WHERE id = %s;", (recipe_id,))
        except:
            pass  # Ignore cleanup errors


@pytest.fixture(scope="function")
def recipe_count():
    """Get the current count of recipes in the database."""
    with get_db_cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM recipes;")
        return cursor.fetchone()["count"]