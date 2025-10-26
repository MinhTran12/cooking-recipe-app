import type { Recipe, RecipeInput } from '@/types';

const API_BASE_URL = 'http://localhost:8000/api';

export interface ApiRecipe {
  id: string;
  title: string;
  image?: string;
  ingredients?: string[];
  instructions?: string[];
  time_to_prepare?: number;
  tags?: string[];
  calories_per_serving?: number;
  serving_size?: number;
  favorite?: boolean;
  created_at: string;
  updated_at: string;
}

export interface ApiRecipeInput {
  title: string;
  image?: string;
  ingredients?: string[];
  instructions?: string[];
  time_to_prepare?: number;
  tags?: string[];
  calories_per_serving?: number;
  serving_size?: number;
  favorite?: boolean;
}

export interface ApiRecipeList {
  recipes: ApiRecipe[];
  total: number;
  limit: number;
  offset: number;
}

class RecipeAPIService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${url}`, error);
      throw error;
    }
  }

  // Get all recipes
  async getAllRecipes(limit: number = 100, offset: number = 0): Promise<ApiRecipeList> {
    return this.request<ApiRecipeList>(`/recipes?limit=${limit}&offset=${offset}`);
  }

  // Get single recipe by ID
  async getRecipeById(id: string): Promise<ApiRecipe> {
    return this.request<ApiRecipe>(`/recipes/${id}`);
  }

  // Create new recipe
  async createRecipe(recipe: ApiRecipeInput): Promise<ApiRecipe> {
    return this.request<ApiRecipe>('/recipes', {
      method: 'POST',
      body: JSON.stringify(recipe),
    });
  }

  // Update existing recipe
  async updateRecipe(id: string, recipe: Partial<ApiRecipeInput>): Promise<ApiRecipe> {
    return this.request<ApiRecipe>(`/recipes/${id}`, {
      method: 'PUT',
      body: JSON.stringify(recipe),
    });
  }

  // Delete recipe
  async deleteRecipe(id: string): Promise<{ id: string; message: string; success: boolean }> {
    return this.request(`/recipes/${id}`, {
      method: 'DELETE',
    });
  }

  // Toggle favorite status
  async toggleFavorite(id: string): Promise<{ id: string; favorite: boolean; message: string }> {
    return this.request(`/recipes/${id}/favorite`, {
      method: 'PATCH',
    });
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request('/health');
  }
}

// Create singleton instance
export const recipeAPI = new RecipeAPIService();

// Helper functions to convert between frontend and backend formats
export function apiRecipeToFrontend(apiRecipe: ApiRecipe): Recipe {
  return {
    id: apiRecipe.id,
    title: apiRecipe.title,
    image: apiRecipe.image,
    ingredients: apiRecipe.ingredients,
    instructions: apiRecipe.instructions,
    timeToPrepare: apiRecipe.time_to_prepare,
    tags: apiRecipe.tags,
    caloriesPerServing: apiRecipe.calories_per_serving,
    servingSize: apiRecipe.serving_size,
    favorite: apiRecipe.favorite,
    createdAt: apiRecipe.created_at,
    updatedAt: apiRecipe.updated_at,
  };
}

export function frontendRecipeToApi(frontendRecipe: RecipeInput): ApiRecipeInput {
  return {
    title: frontendRecipe.title,
    image: frontendRecipe.image,
    ingredients: frontendRecipe.ingredients,
    instructions: frontendRecipe.instructions,
    time_to_prepare: frontendRecipe.timeToPrepare,
    tags: frontendRecipe.tags,
    calories_per_serving: frontendRecipe.caloriesPerServing,
    serving_size: frontendRecipe.servingSize,
    favorite: frontendRecipe.favorite,
  };
}