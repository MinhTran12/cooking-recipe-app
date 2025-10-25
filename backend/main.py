from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from database import test_database_connection
from models import Recipe, RecipeCreate, RecipeUpdate, RecipeList, FavoriteToggle, DeleteResponse
from recipe_service import RecipeService

load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Recipe Manager API",
    description="A REST API for managing cooking recipes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vue dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint - API status check."""
    return {
        "message": "Recipe Manager API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "recipe-manager-api"
    }

# API info endpoint
@app.get("/api/info")
def api_info():
    """API information endpoint."""
    return {
        "name": "Recipe Manager API",
        "version": "1.0.0",
        "description": "REST API for managing cooking recipes",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "database": "/api/database/status",
            "recipes": "/api/recipes",
            "recipe_detail": "/api/recipes/{id}",
            "create_recipe": "POST /api/recipes",
            "update_recipe": "PUT /api/recipes/{id}",
            "delete_recipe": "DELETE /api/recipes/{id}",
            "toggle_favorite": "PATCH /api/recipes/{id}/favorite"
        }
    }

# Database status endpoint
@app.get("/api/database/status")
def database_status():
    """Database connection status and information."""
    try:
        db_info = test_database_connection()
        if db_info["status"] == "error":
            raise HTTPException(status_code=503, detail=db_info)
        return db_info
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "error": f"Database connection failed: {str(e)}"
            }
        )

# Recipe API Endpoints

@app.get("/api/recipes", response_model=RecipeList)
def get_recipes(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of recipes to return"),
    offset: int = Query(default=0, ge=0, description="Number of recipes to skip")
):
    """Get all recipes with pagination."""
    try:
        result = RecipeService.get_all_recipes(limit=limit, offset=offset)
        return RecipeList(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recipes: {str(e)}")

@app.get("/api/recipes/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: str):
    """Get a single recipe by ID."""
    try:
        recipe = RecipeService.get_recipe_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return recipe
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recipe: {str(e)}")

@app.post("/api/recipes", response_model=Recipe, status_code=201)
def create_recipe(recipe_data: RecipeCreate):
    """Create a new recipe."""
    try:
        recipe = RecipeService.create_recipe(recipe_data)
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create recipe: {str(e)}")

@app.put("/api/recipes/{recipe_id}", response_model=Recipe)
def update_recipe(recipe_id: str, recipe_data: RecipeUpdate):
    """Update an existing recipe."""
    try:
        recipe = RecipeService.update_recipe(recipe_id, recipe_data)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return recipe
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update recipe: {str(e)}")

@app.delete("/api/recipes/{recipe_id}", response_model=DeleteResponse)
def delete_recipe(recipe_id: str):
    """Delete a recipe by ID."""
    try:
        deleted = RecipeService.delete_recipe(recipe_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return DeleteResponse(
            id=recipe_id,
            message="Recipe deleted successfully",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete recipe: {str(e)}")

@app.patch("/api/recipes/{recipe_id}/favorite", response_model=FavoriteToggle)
def toggle_recipe_favorite(recipe_id: str):
    """Toggle the favorite status of a recipe."""
    try:
        new_favorite_status = RecipeService.toggle_favorite(recipe_id)
        if new_favorite_status is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return FavoriteToggle(
            id=recipe_id,
            favorite=new_favorite_status,
            message=f"Recipe {'added to' if new_favorite_status else 'removed from'} favorites"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle favorite: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    )