import { describe, it, expect, beforeEach, vi } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useRecipesStore } from "@/stores/recipes";
import type { Recipe, RecipeInput } from "@/types";

// Mock the API service
vi.mock("@/services/recipeAPI", () => ({
  recipeAPI: {
    getAllRecipes: vi.fn(() => Promise.resolve({
      recipes: [
        {
          id: "1",
          title: "Test Recipe 1",
          ingredients: ["ingredient1"],
          instructions: ["step1"],
          tags: ["quick", "pasta"],
          time_to_prepare: 30,
          calories_per_serving: 200,
          serving_size: 2,
          favorite: false
        },
        {
          id: "2", 
          title: "Test Recipe 2",
          ingredients: ["ingredient2"],
          instructions: ["step2"],
          tags: ["slow", "meat"],
          time_to_prepare: 60,
          calories_per_serving: 400,
          serving_size: 4,
          favorite: true
        }
      ]
    })),
    createRecipe: vi.fn((recipe) => Promise.resolve({
      id: "3",
      ...recipe,
      created_at: "2023-01-01T00:00:00Z",
      updated_at: "2023-01-01T00:00:00Z"
    })),
    updateRecipe: vi.fn((id, updates) => Promise.resolve({
      id,
      ...updates,
      updated_at: "2023-01-01T00:00:00Z"
    })),
    deleteRecipe: vi.fn(() => Promise.resolve()),
    toggleFavorite: vi.fn((id) => Promise.resolve({
      id,
      favorite: true // Toggle result
    }))
  },
  frontendRecipeToApi: vi.fn((recipe) => ({
    title: recipe.title,
    ingredients: recipe.ingredients,
    instructions: recipe.instructions,
    tags: recipe.tags,
    time_to_prepare: recipe.timeToPrepare,
    calories_per_serving: recipe.caloriesPerServing,
    serving_size: recipe.servingSize,
    favorite: recipe.favorite
  })),
  apiRecipeToFrontend: vi.fn((recipe) => ({
    id: recipe.id,
    title: recipe.title,
    ingredients: recipe.ingredients,
    instructions: recipe.instructions,
    tags: recipe.tags,
    timeToPrepare: recipe.time_to_prepare,
    caloriesPerServing: recipe.calories_per_serving,
    servingSize: recipe.serving_size,
    favorite: recipe.favorite,
    createdAt: recipe.created_at,
    updatedAt: recipe.updated_at
  }))
}));

describe("Recipes Store", () => {
  beforeEach(() => {
    // Create a fresh pinia instance for each test
    setActivePinia(createPinia());
  });

  describe("State Initialization", () => {
    it("should initialize with default values", () => {
      const store = useRecipesStore();

      expect(store.searchTerm).toBe("");
      expect(store.searchLogic).toBe("AND");
      expect(store.fuzzyThreshold).toBe(100);
      expect(store.recipes).toBeDefined();
      expect(Array.isArray(store.recipes)).toBe(true);
      expect(store.recipes.length).toBe(0); // Starts empty, needs to load from API
      expect(store.loading).toBe(false);
      expect(store.error).toBe(null);
    });
  });

  describe("Basic Actions", () => {
    let store: ReturnType<typeof useRecipesStore>;

    beforeEach(() => {
      store = useRecipesStore();
    });

    it("should set search term", () => {
      store.setSearchTerm("pasta");
      expect(store.searchTerm).toBe("pasta");
    });

    it("should set search logic", () => {
      store.setSearchLogic("OR");
      expect(store.searchLogic).toBe("OR");
    });

    it("should set fuzzy threshold within bounds", () => {
      store.setFuzzyThreshold(50);
      expect(store.fuzzyThreshold).toBe(50);

      // Test bounds
      store.setFuzzyThreshold(-10);
      expect(store.fuzzyThreshold).toBe(0);

      store.setFuzzyThreshold(150);
      expect(store.fuzzyThreshold).toBe(100);
    });
  });

  describe("Recipe Management", () => {
    let store: ReturnType<typeof useRecipesStore>;

    beforeEach(async () => {
      store = useRecipesStore();
      // Load initial recipes
      await store.loadRecipes();
    });

    it("should load recipes from API", async () => {
      // Create a fresh store instance for this test
      setActivePinia(createPinia());
      const store = useRecipesStore();
      expect(store.recipes.length).toBe(0);
      
      await store.loadRecipes();
      
      expect(store.recipes.length).toBeGreaterThanOrEqual(2);
      expect(store.recipes[0].title).toContain("Test Recipe");
    });

    it("should add a new recipe", async () => {
      const initialCount = store.recipes.length;
      const newRecipe: RecipeInput = {
        title: "Test Recipe",
        ingredients: ["ingredient1", "ingredient2"],
        instructions: ["step1", "step2"],
        timeToPrepare: 30,
        tags: ["test"],
        caloriesPerServing: 200,
        servingSize: 2,
      };

      const recipeId = await store.addRecipe(newRecipe);

      expect(store.recipes.length).toBe(initialCount + 1);
      expect(recipeId).toBeDefined();
      expect(store.recipes[0].title).toBe("Test Recipe");
    });

    it("should delete a recipe", async () => {
      const initialCount = store.recipes.length;
      const firstRecipeId = store.recipes[0].id;

      await store.deleteRecipe(firstRecipeId);

      expect(store.recipes.length).toBe(initialCount - 1);
      expect(store.recipes.find((r) => r.id === firstRecipeId)).toBeUndefined();
    });

    it("should update a recipe", async () => {
      const firstRecipe = store.recipes[0];

      await store.updateRecipe(firstRecipe.id, { title: "Updated Title" });

      expect(store.recipes[0].title).toBe("Updated Title");
      expect(store.recipes[0].id).toBe(firstRecipe.id);
    });

    it("should toggle favorite status", async () => {
      const firstRecipe = store.recipes[0];
      const originalFavorite = firstRecipe.favorite;

      await store.toggleFavorite(firstRecipe.id);

      expect(store.recipes[0].favorite).toBe(!originalFavorite);
    });
  });

  describe("Search Functionality", () => {
    let store: ReturnType<typeof useRecipesStore>;

    beforeEach(async () => {
      store = useRecipesStore();
      await store.loadRecipes();
    });

    it("should return all recipes when no search term", () => {
      const filtered = store.filteredRecipes;
      expect(filtered).toEqual(store.recipes);
    });

    it("should filter recipes by exact search (AND logic)", () => {
      store.searchLogic = "AND";
      store.searchTerm = "Test"; // Use "Test" which is in both recipe titles

      const filtered = store.filteredRecipes;
      expect(filtered.length).toBeGreaterThan(0);

      // All filtered recipes should contain 'Test' in title or tags
      filtered.forEach((recipe: Recipe) => {
        const titleMatch = recipe.title.toLowerCase().includes("test");
        const tagMatch = recipe.tags?.some((tag: string) =>
          tag.toLowerCase().includes("test")
        ) || false;
        expect(titleMatch || tagMatch).toBe(true);
      });
    });

    it("should filter recipes by exact search (OR logic)", () => {
      store.searchLogic = "OR";
      store.searchTerm = "quick slow"; // Use tags that exist in our mock data

      const filtered = store.filteredRecipes;
      expect(filtered.length).toBeGreaterThan(0);

      // At least one word should match
      filtered.forEach((recipe) => {
        const hasQuick =
          recipe.title.toLowerCase().includes("quick") ||
          recipe.tags?.some((tag) => tag.toLowerCase().includes("quick")) || false;
        const hasSlow =
          recipe.title.toLowerCase().includes("slow") ||
          recipe.tags?.some((tag) => tag.toLowerCase().includes("slow")) || false;
        expect(hasQuick || hasSlow).toBe(true);
      });
    });

    it("should filter recipes with fuzzy search", () => {
      store.searchTerm = "quick"; // Search for a tag that exists in mock data

      const filtered = store.filteredRecipes;
      expect(filtered.length).toBeGreaterThan(0);

      // Should find recipes with "quick" in tags or title
      const hasQuick = filtered.some(
        (recipe: Recipe) =>
          recipe.title.toLowerCase().includes("quick") ||
          recipe.tags?.some((tag: string) => tag.toLowerCase().includes("quick")) || false
      );
      expect(hasQuick).toBe(true);
    });

    it("should get recipe by id", () => {
      const firstRecipe = store.recipes[0];
      const foundRecipe = store.getById(firstRecipe.id);

      expect(foundRecipe).toEqual(firstRecipe);
    });

    it("should return null for non-existent id", () => {
      const foundRecipe = store.getById("non-existent-id");
      expect(foundRecipe).toBeNull();
    });

    describe("Fuzzy Search Functionality", () => {
      let store: ReturnType<typeof useRecipesStore>;

      beforeEach(async () => {
        store = useRecipesStore();
        await store.loadRecipes();
      });

      it("should find exact matches with high scores", () => {
        store.searchTerm = "quick"; // Use a tag that exists in our mock data

        const filtered = store.filteredRecipes;
        expect(filtered.length).toBeGreaterThan(0);

        // Should find recipes with "quick" in title or tags
        const hasExactMatch = filtered.some(
          (recipe: Recipe) =>
            recipe.title.toLowerCase().includes("quick") ||
            recipe.tags?.some((tag) => tag.toLowerCase().includes("quick")) || false
        );
        expect(hasExactMatch).toBe(true);
      });

      it("should find fuzzy matches with typos", () => {
        store.searchTerm = "quic"; // Partial match for "quick"

        const filtered = store.filteredRecipes;
        expect(filtered.length).toBeGreaterThan(0);

        // Should still find quick recipes despite partial match
        const hasFuzzyMatch = filtered.some(
          (recipe: Recipe) =>
            recipe.title.toLowerCase().includes("quick") ||
            recipe.tags?.some((tag: string) => tag.toLowerCase().includes("quick")) || false
        );
        expect(hasFuzzyMatch).toBe(true);
      });

      it("should respect fuzzy threshold settings", () => {
        store.searchTerm = "qui"; // Partial match

        // Test with low threshold
        store.fuzzyThreshold = 10;
        const lowThresholdResults = store.filteredRecipes;

        // Test with high threshold
        store.fuzzyThreshold = 90;
        const highThresholdResults = store.filteredRecipes;

        // Lower threshold should return more results
        expect(lowThresholdResults.length).toBeGreaterThanOrEqual(
          highThresholdResults.length
        );
      });

      it("should search across title, tags, and ingredients", () => {
        // fuzzy search is always enabled
        store.searchTerm = "quick";

        const filtered = store.filteredRecipes;
        expect(filtered.length).toBeGreaterThan(0);

        // Should find matches in title, tags, or ingredients
        const hasMatch = filtered.some(
          (recipe: Recipe) =>
            recipe.title.toLowerCase().includes("quick") ||
            recipe.tags?.some((tag: string) => tag.toLowerCase().includes("quick")) ||
            recipe.ingredients?.some((ingredient: string) =>
              ingredient.toLowerCase().includes("quick")
            ) || false
        );
        expect(hasMatch).toBe(true);
      });
    });

    it("should handle multi-word queries", () => {
      store.searchTerm = "Test Recipe"; // Use words that appear in our mock data

      const filtered = store.filteredRecipes;
      expect(filtered.length).toBeGreaterThan(0);

      // Should find recipes matching both words
      const hasMultiWordMatch = filtered.some((recipe) => {
        const title = recipe.title.toLowerCase();
        const tags = recipe.tags?.map((t) => t.toLowerCase()) || [];

        const hasTest =
          title.includes("test") || tags.some((t) => t.includes("test"));
        const hasRecipe =
          title.includes("recipe") || tags.some((t) => t.includes("recipe"));

        return hasTest && hasRecipe;
      });
      expect(hasMultiWordMatch).toBe(true);
    });

    it("should return empty results for no matches", () => {
      store.searchTerm = "xyz123nonexistent";

      const filtered = store.filteredRecipes;
      expect(filtered.length).toBe(0);
    });

    it("should handle empty search terms", () => {
      store.searchTerm = "";

      const filtered = store.filteredRecipes;
      // Should return all recipes when search is empty
      expect(filtered.length).toBe(store.recipes.length);
    });
  });
});
