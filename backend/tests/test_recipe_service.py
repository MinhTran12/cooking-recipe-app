from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from recipe_service import RecipeService
from models import Recipe, RecipeCreate, RecipeUpdate


class TestRecipeService:
    """Unit tests for RecipeService methods."""
    
    def test_get_all_recipes_success(self):
        """Test successful retrieval of all recipes."""
        # Mock data
        mock_recipes = [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Test Recipe 1",
                "image": "/test1.jpg",
                "ingredients": ["flour", "sugar"],
                "instructions": ["Mix", "Bake"],
                "time_to_prepare": 30,
                "tags": ["test"],
                "calories_per_serving": 200,
                "serving_size": 4,
                "favorite": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            },
            {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Test Recipe 2",
                "image": "/test2.jpg",
                "ingredients": ["eggs", "milk"],
                "instructions": ["Beat", "Cook"],
                "time_to_prepare": 15,
                "tags": ["quick"],
                "calories_per_serving": 150,
                "serving_size": 2,
                "favorite": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
        ]
        
        with patch('recipe_service.get_db_cursor') as mock_cursor:
            # Setup mock cursor context manager
            mock_ctx = MagicMock()
            mock_cursor.return_value.__enter__.return_value = mock_ctx
            
            # Mock database responses
            mock_ctx.fetchone.return_value = {"total": 2}
            mock_ctx.fetchall.return_value = mock_recipes
            
            # Call the method
            result = RecipeService.get_all_recipes(limit=10, offset=0)
            
            # Assertions
            assert result["total"] == 2
            assert result["limit"] == 10
            assert result["offset"] == 0
            assert len(result["recipes"]) == 2
            assert result["recipes"][0].title == "Test Recipe 1"
            assert result["recipes"][1].title == "Test Recipe 2"
            
            # Verify SQL queries were called
            assert mock_ctx.execute.call_count == 2
    
    def test_get_recipe_by_id_found(self):
        """Test successful retrieval of a recipe by ID."""
        mock_recipe = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Found Recipe",
            "image": "/found.jpg",
            "ingredients": ["ingredient1", "ingredient2"],
            "instructions": ["step1", "step2"],
            "time_to_prepare": 25,
            "tags": ["found"],
            "calories_per_serving": 300,
            "serving_size": 3,
            "favorite": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        with patch('recipe_service.get_db_cursor') as mock_cursor:
            mock_ctx = MagicMock()
            mock_cursor.return_value.__enter__.return_value = mock_ctx
            mock_ctx.fetchone.return_value = mock_recipe
            
            # Call the method
            result = RecipeService.get_recipe_by_id("123e4567-e89b-12d3-a456-426614174000")
            
            # Assertions
            assert result is not None
            assert isinstance(result, Recipe)
            assert result.title == "Found Recipe"
            assert result.id == "123e4567-e89b-12d3-a456-426614174000"
            assert result.favorite is True
    
    def test_get_recipe_by_id_not_found(self):
        """Test retrieval of a non-existent recipe by ID."""
        with patch('recipe_service.get_db_cursor') as mock_cursor:
            mock_ctx = MagicMock()
            mock_cursor.return_value.__enter__.return_value = mock_ctx
            mock_ctx.fetchone.return_value = None
            
            # Call the method
            result = RecipeService.get_recipe_by_id("non-existent-id")
            
            # Assertions
            assert result is None
    
    @patch('recipe_service.uuid.uuid4')
    @patch('recipe_service.datetime')
    def test_create_recipe_success(self, mock_datetime, mock_uuid):
        """Test successful recipe creation."""
        # Setup mocks
        mock_uuid.return_value = "new-recipe-id"
        mock_time = datetime.now(timezone.utc)
        mock_datetime.now.return_value = mock_time
        
        recipe_data = RecipeCreate(
            title="New Recipe",
            image="/new.jpg",
            ingredients=["new ingredient"],
            instructions=["new step"],
            time_to_prepare=20,
            tags=["new"],
            calories_per_serving = 250,
            serving_size=2,
            favorite=False
        )
        
        mock_created_recipe = {
            "id": "new-recipe-id",
            "title": "New Recipe",
            "image": "/new.jpg",
            "ingredients": ["new ingredient"],
            "instructions": ["new step"],
            "time_to_prepare": 20,
            "tags": ["new"],
            "calories_per_serving": 250,
            "serving_size": 2,
            "favorite": False,
            "created_at": mock_time,
            "updated_at": mock_time
        }
        
        with patch('recipe_service.get_db_cursor') as mock_cursor:
            mock_ctx = MagicMock()
            mock_cursor.return_value.__enter__.return_value = mock_ctx
            mock_ctx.fetchone.return_value = mock_created_recipe
            
            # Call the method
            result = RecipeService.create_recipe(recipe_data)
            
            # Assertions
            assert result.title == "New Recipe"
            assert result.id == "new-recipe-id"
            assert mock_ctx.execute.called
    
    def test_update_recipe_success(self):
        """Test successful recipe update."""
        recipe_id = "123e4567-e89b-12d3-a456-426614174000"
        update_data = RecipeUpdate(title="Updated Recipe", favorite=True)
        
        mock_updated_recipe = {
            "id": recipe_id,
            "title": "Updated Recipe",
            "image": "/original.jpg",
            "ingredients": ["original ingredient"],
            "instructions": ["original step"],
            "time_to_prepare": 30,
            "tags": ["original"],
            "calories_per_serving": 300,
            "serving_size": 4,
            "favorite": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        with patch('recipe_service.get_db_cursor') as mock_cursor:
            mock_ctx = MagicMock()
            mock_cursor.return_value.__enter__.return_value = mock_ctx
            mock_ctx.fetchone.return_value = mock_updated_recipe
            
            # Call the method
            result = RecipeService.update_recipe(recipe_id, update_data)
            
            # Assertions
            assert result is not None
            assert result.title == "Updated Recipe"
            assert result.favorite is True
    
    def test_update_recipe_not_found(self):
        """Test updating a non-existent recipe."""
        update_data = RecipeUpdate(title="Updated Recipe")
        
        with patch('recipe_service.get_db_cursor') as mock_cursor:
            mock_ctx = MagicMock()
            mock_cursor.return_value.__enter__.return_value = mock_ctx
            mock_ctx.fetchone.return_value = None
            
            # Call the method
            result = RecipeService.update_recipe("non-existent-id", update_data)
            
            # Assertions
            assert result is None
    
    def test_delete_recipe_success(self):
        """Test successful recipe deletion."""
        with patch('recipe_service.get_db_cursor') as mock_cursor:
            mock_ctx = MagicMock()
            mock_cursor.return_value.__enter__.return_value = mock_ctx
            mock_ctx.rowcount = 1  # Simulate one row deleted
            
            # Call the method
            result = RecipeService.delete_recipe("existing-id")
            
            # Assertions
            assert result is True
    
    def test_delete_recipe_not_found(self):
        """Test deleting a non-existent recipe."""
        with patch('recipe_service.get_db_cursor') as mock_cursor:
            mock_ctx = MagicMock()
            mock_cursor.return_value.__enter__.return_value = mock_ctx
            mock_ctx.rowcount = 0  # Simulate no rows deleted
            
            # Call the method
            result = RecipeService.delete_recipe("non-existent-id")
            
            # Assertions
            assert result is False
    
    def test_toggle_favorite_success(self):
        """Test successful favorite toggle."""
        with patch('recipe_service.get_db_cursor') as mock_cursor:
            mock_ctx = MagicMock()
            mock_cursor.return_value.__enter__.return_value = mock_ctx
            mock_ctx.fetchone.return_value = {"favorite": True}
            
            # Call the method
            result = RecipeService.toggle_favorite("existing-id")
            
            # Assertions
            assert result is True
    
    def test_toggle_favorite_not_found(self):
        """Test toggling favorite for non-existent recipe."""
        with patch('recipe_service.get_db_cursor') as mock_cursor:
            mock_ctx = MagicMock()
            mock_cursor.return_value.__enter__.return_value = mock_ctx
            mock_ctx.fetchone.return_value = None
            
            # Call the method
            result = RecipeService.toggle_favorite("non-existent-id")
            
            # Assertions
            assert result is None