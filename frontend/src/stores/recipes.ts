import { defineStore } from "pinia";
import { recipeAPI, apiRecipeToFrontend, frontendRecipeToApi } from "@/services/recipeAPI";
import type { Recipe, RecipesState, SearchLogic, FuzzyMatchResult, RecipeInput } from "@/types";

// Fuzzy search utility functions
const fuzzyMatch = (text: string, query: string): FuzzyMatchResult => {
  const textLower = text.toLowerCase();
  const queryLower = query.toLowerCase();

  // Exact match gets highest score
  if (textLower.includes(queryLower)) {
    return { score: 100, matched: true };
  }

  // Check for character sequence match (fuzzy)
  let textIndex = 0;
  let queryIndex = 0;
  let score = 0;
  let consecutiveMatches = 0;

  while (textIndex < textLower.length && queryIndex < queryLower.length) {
    if (textLower[textIndex] === queryLower[queryIndex]) {
      score += 10;
      if (consecutiveMatches > 0) {
        score += consecutiveMatches * 2; // Bonus for consecutive matches
      }
      consecutiveMatches++;
      queryIndex++;
    } else {
      consecutiveMatches = 0;
    }
    textIndex++;
  }

  // If we matched all query characters
  if (queryIndex === queryLower.length) {
    return { score, matched: true };
  }

  return { score: 0, matched: false };
};

const calculateFuzzyScore = (recipe: Recipe, query: string): number => {
  const words = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
  if (words.length === 0) return 0;

  let totalScore = 0;
  let matchedWords = 0;

  for (const word of words) {
    let bestScore = 0;
    let wordMatched = false;

    // Check title
    const titleMatch = fuzzyMatch(recipe.title, word);
    if (titleMatch.matched) {
      bestScore = Math.max(bestScore, titleMatch.score * 1.5); // Title gets higher weight
      wordMatched = true;
    }

    // Check tags
    if (recipe.tags) {
      for (const tag of recipe.tags) {
        const tagMatch = fuzzyMatch(tag, word);
        if (tagMatch.matched) {
          bestScore = Math.max(bestScore, tagMatch.score);
          wordMatched = true;
        }
      }
    }

    // Check ingredients
    if (recipe.ingredients) {
      for (const ingredient of recipe.ingredients) {
        const ingredientMatch = fuzzyMatch(ingredient, word);
        if (ingredientMatch.matched) {
          bestScore = Math.max(bestScore, ingredientMatch.score * 0.8); // Ingredients get lower weight
          wordMatched = true;
        }
      }
    }

    if (wordMatched) {
      totalScore += bestScore;
      matchedWords++;
    }
  }

  // Return score only if at least one word matched
  return matchedWords > 0 ? totalScore : 0;
};

// Pinia store for managing recipes with API integration
export const useRecipesStore = defineStore("recipes", {
  state: (): RecipesState => ({
    recipes: [],
    searchTerm: "",
    searchLogic: "AND" as SearchLogic,
    fuzzyThreshold: 100,
    loading: false,
    error: null,
  }),
  getters: {
    filteredRecipes(state): Recipe[] {
      const q = state.searchTerm.trim();
      if (!q) return state.recipes;

      const words = q.toLowerCase().split(/\s+/).filter(Boolean);

      // Always use fuzzy search logic
      return state.recipes.filter((recipe) => {
        if (state.searchLogic === "AND") {
          return words.every(
            (word) => calculateFuzzyScore(recipe, word) >= state.fuzzyThreshold
          );
        } else {
          return words.some(
            (word) => calculateFuzzyScore(recipe, word) >= state.fuzzyThreshold
          );
        }
      });
    },
    getById: (state) => (id: string): Recipe | null => state.recipes.find((r) => r.id === id) || null,
  },
  actions: {
    setSearchTerm(v: string): void {
      this.searchTerm = v;
    },
    setSearchLogic(v: SearchLogic): void {
      this.searchLogic = v;
    },
    setFuzzyThreshold(v: number): void {
      this.fuzzyThreshold = Math.max(0, Math.min(100, v));
    },

    // API Actions
    async loadRecipes(): Promise<void> {
      this.loading = true;
      this.error = null;
      try {
        const apiResult = await recipeAPI.getAllRecipes();
        this.recipes = apiResult.recipes.map(apiRecipeToFrontend);
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to load recipes';
        console.error('Failed to load recipes:', error);
      } finally {
        this.loading = false;
      }
    },

    async addRecipe(partial: RecipeInput): Promise<string> {
      this.loading = true;
      this.error = null;
      try {
        const apiRecipeInput = frontendRecipeToApi(partial);
        const apiRecipe = await recipeAPI.createRecipe(apiRecipeInput);
        const recipe = apiRecipeToFrontend(apiRecipe);
        this.recipes.unshift(recipe);
        return recipe.id;
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to create recipe';
        console.error('Failed to create recipe:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async deleteRecipe(id: string): Promise<void> {
      this.loading = true;
      this.error = null;
      try {
        await recipeAPI.deleteRecipe(id);
        const i = this.recipes.findIndex((r) => r.id === id);
        if (i !== -1) this.recipes.splice(i, 1);
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to delete recipe';
        console.error('Failed to delete recipe:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateRecipe(id: string, patch: Partial<RecipeInput>): Promise<void> {
      this.loading = true;
      this.error = null;
      try {
        const apiRecipeInput = frontendRecipeToApi(patch as RecipeInput);
        const apiRecipe = await recipeAPI.updateRecipe(id, apiRecipeInput);
        const updatedRecipe = apiRecipeToFrontend(apiRecipe);
        
        const i = this.recipes.findIndex((r) => r.id === id);
        if (i !== -1) {
          this.recipes[i] = updatedRecipe;
        }
      } catch (error) {
        this.error = error instanceof Error ? error.message : 'Failed to update recipe';
        console.error('Failed to update recipe:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async toggleFavorite(id: string): Promise<void> {
      // Find the recipe
      const i = this.recipes.findIndex((r) => r.id === id);
      if (i === -1) return;

      // Store original state for potential rollback
      const originalFavoriteState = this.recipes[i].favorite;
      
      // Optimistically update UI immediately
      this.recipes[i].favorite = !originalFavoriteState;

      try {
        // Make API call in background
        const result = await recipeAPI.toggleFavorite(id);
        // Ensure our optimistic update matches the server response
        this.recipes[i].favorite = result.favorite;
      } catch (error) {
        // Rollback on failure
        this.recipes[i].favorite = originalFavoriteState;
        
        // Show error without affecting loading state
        console.error('Failed to toggle favorite:', error);
        
        // Optionally show a non-intrusive error (toast notification)
        // this.showToast('Failed to update favorite status');
        
        throw error;
      }
      // Note: NO loading state changes - keeps UI smooth
    },
  },
});
