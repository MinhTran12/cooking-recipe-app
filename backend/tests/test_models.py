import pytest
from datetime import datetime
from pydantic import ValidationError
from models import Recipe, RecipeCreate, RecipeUpdate, RecipeList, FavoriteToggle, DeleteResponse


class TestPydanticModels:
    """Unit tests for Pydantic model validation."""
    
    def test_recipe_create_valid_data(self):
        """Test RecipeCreate with valid data."""
        valid_data = {
            "title": "Test Recipe",
            "image": "/test.jpg",
            "ingredients": ["flour", "sugar", "eggs"],
            "instructions": ["Mix ingredients", "Bake for 30 minutes"],
            "time_to_prepare": 30,
            "tags": ["dessert", "sweet"],
            "calories_per_serving": 250,
            "serving_size": 8,
            "favorite": False
        }
        
        recipe = RecipeCreate(**valid_data)
        
        assert recipe.title == "Test Recipe"
        assert recipe.ingredients == ["flour", "sugar", "eggs"]
        assert recipe.time_to_prepare == 30
        assert recipe.favorite is False
    
    def test_recipe_create_missing_required_fields(self):
        """Test RecipeCreate fails with missing required fields."""
        invalid_data = {
            "title": "Test Recipe"
            # Missing required fields: ingredients, instructions, etc.
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**invalid_data)
        
        errors = exc_info.value.errors()
        missing_fields = [error["loc"][0] for error in errors if error["type"] == "missing"]
        
        assert "ingredients" in missing_fields
        assert "instructions" in missing_fields
        assert "time_to_prepare" in missing_fields
        assert "calories_per_serving" in missing_fields
        assert "serving_size" in missing_fields
    
    def test_recipe_create_invalid_field_types(self):
        """Test RecipeCreate fails with invalid field types."""
        invalid_data = {
            "title": "",  # Empty string should fail min_length validation
            "ingredients": [],  # Empty list should fail min_length validation
            "instructions": [],  # Empty list should fail min_length validation
            "time_to_prepare": 0,  # Should fail ge=1 validation
            "calories_per_serving": 0,  # Should fail ge=1 validation
            "serving_size": 0,  # Should fail ge=1 validation
        }
        
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(**invalid_data)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
    
    def test_recipe_create_with_defaults(self):
        """Test RecipeCreate uses default values correctly."""
        minimal_data = {
            "title": "Minimal Recipe",
            "ingredients": ["ingredient1"],
            "instructions": ["step1"],
            "time_to_prepare": 15,
            "calories_per_serving": 100,
            "serving_size": 1
        }
        
        recipe = RecipeCreate(**minimal_data)
        
        assert recipe.tags == []  # Should default to empty list
        assert recipe.favorite is False  # Should default to False
        assert recipe.image is None  # Should default to None
    
    def test_recipe_update_all_optional(self):
        """Test RecipeUpdate allows all fields to be optional."""
        # Empty update should be valid
        update = RecipeUpdate()
        assert update.title is None
        assert update.ingredients is None
        
        # Partial update should be valid
        partial_update = RecipeUpdate(title="Updated Title", favorite=True)
        assert partial_update.title == "Updated Title"
        assert partial_update.favorite is True
        assert partial_update.ingredients is None
    
    def test_recipe_model_with_all_fields(self):
        """Test Recipe model with all required database fields."""
        recipe_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Complete Recipe",
            "image": "/complete.jpg",
            "ingredients": ["ingredient1", "ingredient2"],
            "instructions": ["step1", "step2"],
            "time_to_prepare": 45,
            "tags": ["tag1", "tag2"],
            "calories_per_serving": 300,
            "serving_size": 4,
            "favorite": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        recipe = Recipe(**recipe_data)
        
        assert recipe.id == "123e4567-e89b-12d3-a456-426614174000"
        assert recipe.title == "Complete Recipe"
        assert len(recipe.ingredients) == 2
        assert len(recipe.instructions) == 2
        assert recipe.favorite is True
    
    def test_recipe_list_model(self):
        """Test RecipeList model structure."""
        recipe_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "List Recipe",
            "image": None,
            "ingredients": ["ingredient1"],
            "instructions": ["step1"],
            "time_to_prepare": 20,
            "tags": [],
            "calories_per_serving": 200,
            "serving_size": 2,
            "favorite": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        recipe_list_data = {
            "recipes": [Recipe(**recipe_data)],
            "total": 1,
            "limit": 10,
            "offset": 0
        }
        
        recipe_list = RecipeList(**recipe_list_data)
        
        assert len(recipe_list.recipes) == 1
        assert recipe_list.total == 1
        assert recipe_list.limit == 10
        assert recipe_list.offset == 0
    
    def test_favorite_toggle_model(self):
        """Test FavoriteToggle model."""
        toggle_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "favorite": True,
            "message": "Recipe added to favorites"
        }
        
        toggle = FavoriteToggle(**toggle_data)
        
        assert toggle.id == "123e4567-e89b-12d3-a456-426614174000"
        assert toggle.favorite is True
        assert "added to favorites" in toggle.message
    
    def test_delete_response_model(self):
        """Test DeleteResponse model."""
        delete_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "message": "Recipe deleted successfully",
            "success": True
        }
        
        delete_response = DeleteResponse(**delete_data)
        
        assert delete_response.id == "123e4567-e89b-12d3-a456-426614174000"
        assert delete_response.success is True
        assert "deleted successfully" in delete_response.message
    
    def test_field_validation_constraints(self):
        """Test various field validation constraints."""
        # Test title length constraint
        with pytest.raises(ValidationError):
            RecipeCreate(
                title="x" * 256,  # Too long (max 255)
                ingredients=["test"],
                instructions=["test"],
                time_to_prepare=10,
                calories_per_serving=100,
                serving_size=1
            )
        
        # Test image URL length constraint
        with pytest.raises(ValidationError):
            RecipeCreate(
                title="Test",
                image="x" * 501,  # Too long (max 500)
                ingredients=["test"],
                instructions=["test"],
                time_to_prepare=10,
                calories_per_serving=100,
                serving_size=1
            )