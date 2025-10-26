class TestRecipeAPIIntegration:
    """Integration tests for Recipe API endpoints using real database."""
    
    def test_get_recipes_success(self, client, recipe_count):
        """Test GET /api/recipes returns recipes successfully."""
        response = client.get("/api/recipes")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "recipes" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        
        # Check that we get some recipes (from seeded data)
        assert data["total"] >= 0
        assert data["limit"] == 100  # default limit
        assert data["offset"] == 0   # default offset
        assert len(data["recipes"]) <= data["total"]
        
        # If we have recipes, check the structure of the first one
        if data["recipes"]:
            recipe = data["recipes"][0]
            required_fields = [
                "id", "title", "ingredients", "instructions", 
                "time_to_prepare", "tags", "calories_per_serving", 
                "serving_size", "favorite", "created_at", "updated_at"
            ]
            for field in required_fields:
                assert field in recipe
    
    def test_get_recipes_with_pagination(self, client):
        """Test GET /api/recipes with pagination parameters."""
        response = client.get("/api/recipes?limit=5&offset=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["limit"] == 5
        assert data["offset"] == 2
        assert len(data["recipes"]) <= 5
    
    def test_create_recipe_success(self, client, sample_recipe_data):
        """Test POST /api/recipes creates a new recipe."""
        response = client.post("/api/recipes", json=sample_recipe_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Check that recipe was created with correct data
        assert data["title"] == sample_recipe_data["title"]
        assert data["ingredients"] == sample_recipe_data["ingredients"]
        assert data["instructions"] == sample_recipe_data["instructions"]
        assert data["time_to_prepare"] == sample_recipe_data["time_to_prepare"]
        assert data["tags"] == sample_recipe_data["tags"]
        assert data["calories_per_serving"] == sample_recipe_data["calories_per_serving"]
        assert data["serving_size"] == sample_recipe_data["serving_size"]
        assert data["favorite"] == sample_recipe_data["favorite"]
        
        # Check that ID and timestamps were generated
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Cleanup: delete the created recipe
        recipe_id = data["id"]
        delete_response = client.delete(f"/api/recipes/{recipe_id}")
        assert delete_response.status_code == 200
    
    def test_create_minimal_recipe_success(self, client, minimal_recipe_data):
        """Test POST /api/recipes creates a recipe with only title."""
        response = client.post("/api/recipes", json=minimal_recipe_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Check that recipe was created with correct data
        assert data["title"] == minimal_recipe_data["title"]
        
        # Check that optional fields are None/default
        assert data["ingredients"] is None
        assert data["instructions"] is None
        assert data["time_to_prepare"] is None
        assert data["tags"] is None
        assert data["calories_per_serving"] is None
        assert data["serving_size"] is None
        assert data["favorite"] is False  # Default value
        assert data["image"] is None
        
        # Check that ID and timestamps were generated
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        
        # Cleanup: delete the created recipe
        recipe_id = data["id"]
        delete_response = client.delete(f"/api/recipes/{recipe_id}")
        assert delete_response.status_code == 200
    
    def test_create_recipe_invalid_data(self, client):
        """Test POST /api/recipes with invalid data returns validation error."""
        invalid_data = {
            "title": "",  # Empty title should fail validation
            "time_to_prepare": -5  # Negative time should fail validation when provided
        }
        
        response = client.post("/api/recipes", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
        assert "detail" in response.json()
    
    def test_get_recipe_by_id_success(self, client, clean_test_recipe, sample_recipe_data):
        """Test GET /api/recipes/{id} returns specific recipe."""
        # Create a test recipe
        recipe_id = clean_test_recipe(sample_recipe_data)
        
        response = client.get(f"/api/recipes/{recipe_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == recipe_id
        assert data["title"] == sample_recipe_data["title"]
        assert data["ingredients"] == sample_recipe_data["ingredients"]
    
    def test_get_recipe_by_id_not_found(self, client):
        """Test GET /api/recipes/{id} with non-existent ID returns 404."""
        non_existent_id = "123e4567-e89b-12d3-a456-426614174999"
        response = client.get(f"/api/recipes/{non_existent_id}")
        
        assert response.status_code == 404
        assert "Recipe not found" in response.json()["detail"]
    
    def test_update_recipe_success(self, client, clean_test_recipe, sample_recipe_data, updated_recipe_data):
        """Test PUT /api/recipes/{id} updates existing recipe."""
        # Create a test recipe
        recipe_id = clean_test_recipe(sample_recipe_data)
        
        response = client.put(f"/api/recipes/{recipe_id}", json=updated_recipe_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == recipe_id
        assert data["title"] == updated_recipe_data["title"]
        assert data["time_to_prepare"] == updated_recipe_data["time_to_prepare"]
        assert data["favorite"] == updated_recipe_data["favorite"]
        
        # Verify original data is preserved for fields not updated
        assert data["ingredients"] == sample_recipe_data["ingredients"]
        assert data["instructions"] == sample_recipe_data["instructions"]
    
    def test_update_recipe_not_found(self, client, updated_recipe_data):
        """Test PUT /api/recipes/{id} with non-existent ID returns 404."""
        non_existent_id = "123e4567-e89b-12d3-a456-426614174999"
        response = client.put(f"/api/recipes/{non_existent_id}", json=updated_recipe_data)
        
        assert response.status_code == 404
        assert "Recipe not found" in response.json()["detail"]
    
    def test_delete_recipe_success(self, client, clean_test_recipe, sample_recipe_data):
        """Test DELETE /api/recipes/{id} deletes existing recipe."""
        # Create a test recipe
        recipe_id = clean_test_recipe(sample_recipe_data)
        
        response = client.delete(f"/api/recipes/{recipe_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == recipe_id
        assert data["success"] is True
        assert "deleted successfully" in data["message"]
        
        # Verify recipe is actually deleted
        get_response = client.get(f"/api/recipes/{recipe_id}")
        assert get_response.status_code == 404
    
    def test_delete_recipe_not_found(self, client):
        """Test DELETE /api/recipes/{id} with non-existent ID returns 404."""
        non_existent_id = "123e4567-e89b-12d3-a456-426614174999"
        response = client.delete(f"/api/recipes/{non_existent_id}")
        
        assert response.status_code == 404
        assert "Recipe not found" in response.json()["detail"]
    
    def test_toggle_favorite_success(self, client, clean_test_recipe, sample_recipe_data):
        """Test PATCH /api/recipes/{id}/favorite toggles favorite status."""
        # Create a test recipe (favorite = False by default)
        recipe_id = clean_test_recipe(sample_recipe_data)
        
        response = client.patch(f"/api/recipes/{recipe_id}/favorite")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == recipe_id
        assert data["favorite"] is True  # Should be toggled to True
        assert "added to favorites" in data["message"]
        
        # Toggle again
        response2 = client.patch(f"/api/recipes/{recipe_id}/favorite")
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        assert data2["favorite"] is False  # Should be toggled back to False
        assert "removed from favorites" in data2["message"]
    
    def test_toggle_favorite_not_found(self, client):
        """Test PATCH /api/recipes/{id}/favorite with non-existent ID returns 404."""
        non_existent_id = "123e4567-e89b-12d3-a456-426614174999"
        response = client.patch(f"/api/recipes/{non_existent_id}/favorite")
        
        assert response.status_code == 404
        assert "Recipe not found" in response.json()["detail"]
    
    def test_health_endpoint(self, client):
        """Test GET /health endpoint works."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "recipe-manager-api"
    
    def test_api_info_endpoint(self, client):
        """Test GET /api/info endpoint works."""
        response = client.get("/api/info")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Recipe Manager API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
    
    def test_database_status_endpoint(self, client):
        """Test GET /api/database/status endpoint works."""
        response = client.get("/api/database/status")
        
        # This test depends on database being available
        # It could be 200 (success) or 503 (database unavailable)
        assert response.status_code in [200, 503]
        
        data = response.json()
        assert "status" in data
        
        if response.status_code == 200:
            assert data["status"] == "connected"
            assert "database_version" in data
            assert "recipe_count" in data