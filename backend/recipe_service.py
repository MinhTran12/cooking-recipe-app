"""Recipe service layer for database operations."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from database import get_db_cursor
from models import Recipe, RecipeCreate, RecipeUpdate


class RecipeService:
    """Service class for recipe database operations."""
    
    @staticmethod
    def get_all_recipes(limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Get all recipes with pagination.
        
        Args:
            limit: Maximum number of recipes to return
            offset: Number of recipes to skip
            
        Returns:
            Dict containing recipes list and pagination info
        """
        with get_db_cursor() as cursor:
            # Get total count
            cursor.execute("SELECT COUNT(*) as total FROM recipes;")
            total = cursor.fetchone()['total']
            
            # Get recipes with pagination
            cursor.execute("""
                SELECT id, title, image, ingredients, instructions, time_to_prepare, 
                       tags, calories_per_serving, serving_size, favorite, created_at, updated_at
                FROM recipes 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s;
            """, (limit, offset))
            
            recipes_data = cursor.fetchall()
            recipes = [Recipe.model_validate(dict(row)) for row in recipes_data]
            
            return {
                "recipes": recipes,
                "total": total,
                "limit": limit,
                "offset": offset
            }
    
    @staticmethod
    def get_recipe_by_id(recipe_id: str) -> Optional[Recipe]:
        """
        Get a single recipe by ID.
        
        Args:
            recipe_id: Recipe UUID
            
        Returns:
            Recipe object or None if not found
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, title, image, ingredients, instructions, time_to_prepare, 
                       tags, calories_per_serving, serving_size, favorite, created_at, updated_at
                FROM recipes 
                WHERE id = %s;
            """, (recipe_id,))
            
            row = cursor.fetchone()
            if row:
                return Recipe.model_validate(dict(row))
            return None
    
    @staticmethod
    def create_recipe(recipe_data: RecipeCreate) -> Recipe:
        """
        Create a new recipe.
        
        Args:
            recipe_data: Recipe creation data
            
        Returns:
            Created recipe object
        """
        recipe_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                INSERT INTO recipes (
                    id, title, image, ingredients, instructions, time_to_prepare, 
                    tags, calories_per_serving, serving_size, favorite, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING *;
            """, (
                recipe_id,
                recipe_data.title,
                recipe_data.image,
                recipe_data.ingredients,
                recipe_data.instructions,
                recipe_data.time_to_prepare,
                recipe_data.tags,
                recipe_data.calories_per_serving,
                recipe_data.serving_size,
                recipe_data.favorite,
                now,
                now
            ))
            
            row = cursor.fetchone()
            return Recipe.model_validate(dict(row))
    
    @staticmethod
    def update_recipe(recipe_id: str, recipe_data: RecipeUpdate) -> Optional[Recipe]:
        """
        Update an existing recipe.
        
        Args:
            recipe_id: Recipe UUID
            recipe_data: Recipe update data
            
        Returns:
            Updated recipe object or None if not found
        """
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []
        
        for field, value in recipe_data.model_dump(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if not update_fields:
            # No fields to update, return existing recipe
            return RecipeService.get_recipe_by_id(recipe_id)
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = %s")
        values.append(datetime.now(timezone.utc))
        values.append(recipe_id)
        
        with get_db_cursor() as cursor:
            cursor.execute(f"""
                UPDATE recipes 
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING *;
            """, values)
            
            row = cursor.fetchone()
            if row:
                return Recipe.model_validate(dict(row))
            return None
    
    @staticmethod
    def delete_recipe(recipe_id: str) -> bool:
        """
        Delete a recipe by ID.
        
        Args:
            recipe_id: Recipe UUID
            
        Returns:
            True if deleted, False if not found
        """
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM recipes WHERE id = %s;", (recipe_id,))
            return cursor.rowcount > 0
    
    @staticmethod
    def toggle_favorite(recipe_id: str) -> Optional[bool]:
        """
        Toggle the favorite status of a recipe.
        
        Args:
            recipe_id: Recipe UUID
            
        Returns:
            New favorite status or None if recipe not found
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                UPDATE recipes 
                SET favorite = NOT favorite, updated_at = %s
                WHERE id = %s
                RETURNING favorite;
            """, (datetime.now(timezone.utc), recipe_id))
            
            row = cursor.fetchone()
            if row:
                return row['favorite']
            return None