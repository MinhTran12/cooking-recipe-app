"""Pydantic models for the Recipe Manager API."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class RecipeBase(BaseModel):
    """Base recipe model with common fields."""
    title: str = Field(..., min_length=1, max_length=255)
    image: Optional[str] = Field(None, max_length=500)
    ingredients: List[str] = Field(..., min_length=1)
    instructions: List[str] = Field(..., min_length=1)
    time_to_prepare: int = Field(..., ge=1, description="Time to prepare in minutes")
    tags: List[str] = Field(default_factory=list)
    calories_per_serving: int = Field(..., ge=1, description="Calories per serving")
    serving_size: int = Field(..., ge=1, description="Number of servings")
    favorite: bool = Field(default=False)


class RecipeCreate(RecipeBase):
    """Model for creating a new recipe."""
    pass


class RecipeUpdate(BaseModel):
    """Model for updating an existing recipe (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    image: Optional[str] = Field(None, max_length=500)
    ingredients: Optional[List[str]] = Field(None, min_length=1)
    instructions: Optional[List[str]] = Field(None, min_length=1)
    time_to_prepare: Optional[int] = Field(None, ge=1)
    tags: Optional[List[str]] = None
    calories_per_serving: Optional[int] = Field(None, ge=1)
    serving_size: Optional[int] = Field(None, ge=1)
    favorite: Optional[bool] = None


class Recipe(RecipeBase):
    """Complete recipe model with database fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Unique recipe identifier")
    created_at: datetime = Field(..., description="Recipe creation timestamp")
    updated_at: datetime = Field(..., description="Recipe last update timestamp")


class RecipeList(BaseModel):
    """Model for recipe list responses."""
    recipes: List[Recipe]
    total: int = Field(..., description="Total number of recipes")
    limit: int = Field(..., description="Number of recipes per page")
    offset: int = Field(..., description="Number of recipes skipped")


class FavoriteToggle(BaseModel):
    """Model for favorite toggle response."""
    id: str
    favorite: bool
    message: str


class DeleteResponse(BaseModel):
    """Model for delete operation response."""
    id: str
    message: str
    success: bool