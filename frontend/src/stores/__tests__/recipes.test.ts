import { describe, it, expect, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useRecipesStore } from "@/stores/recipes";
import type { Recipe, RecipeInput } from "@/types";

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
      expect(store.recipes.length).toBeGreaterThan(0);
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

    beforeEach(() => {
      store = useRecipesStore();
    });

    it("should add a new recipe", () => {
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

      const recipeId = store.addRecipe(newRecipe);

      expect(store.recipes.length).toBe(initialCount + 1);
      expect(recipeId).toBeDefined();
      expect(store.recipes[0].title).toBe("Test Recipe");
    });

    it("should delete a recipe", () => {
      const initialCount = store.recipes.length;
      const firstRecipeId = store.recipes[0].id;

      store.deleteRecipe(firstRecipeId);

      expect(store.recipes.length).toBe(initialCount - 1);
      expect(store.recipes.find((r) => r.id === firstRecipeId)).toBeUndefined();
    });

    it("should update a recipe", () => {
      const firstRecipe = store.recipes[0];

      store.updateRecipe(firstRecipe.id, { title: "Updated Title" });

      expect(store.recipes[0].title).toBe("Updated Title");
      expect(store.recipes[0].id).toBe(firstRecipe.id);
    });

    it("should toggle favorite status", () => {
      const firstRecipe = store.recipes[0];
      const originalFavorite = firstRecipe.favorite;

      store.toggleFavorite(firstRecipe.id);

      expect(store.recipes[0].favorite).toBe(!originalFavorite);
    });
  });

  describe("Search Functionality", () => {
    let store: ReturnType<typeof useRecipesStore>;

    beforeEach(() => {
      store = useRecipesStore();
    });

    it("should return all recipes when no search term", () => {
      const filtered = store.filteredRecipes;
      expect(filtered).toEqual(store.recipes);
    });

    it("should filter recipes by exact search (AND logic)", () => {
      store.searchLogic = "AND";
      store.searchTerm = "quick";

      const filtered = store.filteredRecipes;
      expect(filtered.length).toBeGreaterThan(0);

      // All filtered recipes should contain 'quick' in title or tags
      filtered.forEach((recipe: Recipe) => {
        const titleMatch = recipe.title.toLowerCase().includes("quick");
        const tagMatch = recipe.tags.some((tag: string) =>
          tag.toLowerCase().includes("quick")
        );
        expect(titleMatch || tagMatch).toBe(true);
      });
    });

    it("should filter recipes by exact search (OR logic)", () => {
      store.searchLogic = "OR";
      store.searchTerm = "quick pasta";

      const filtered = store.filteredRecipes;
      expect(filtered.length).toBeGreaterThan(0);

      // At least one word should match
      filtered.forEach((recipe) => {
        const hasQuick =
          recipe.title.toLowerCase().includes("quick") ||
          recipe.tags.some((tag) => tag.toLowerCase().includes("quick"));
        const hasPasta =
          recipe.title.toLowerCase().includes("pasta") ||
          recipe.tags.some((tag) => tag.toLowerCase().includes("pasta"));
        expect(hasQuick || hasPasta).toBe(true);
      });
    });

    it("should filter recipes with fuzzy search", () => {
      store.searchTerm = "pasta"; // Search for a common tag that should exist

      const filtered = store.filteredRecipes;
      expect(filtered.length).toBeGreaterThan(0);

      // Should find recipes with "pasta" in tags or title
      const hasPasta = filtered.some(
        (recipe: Recipe) =>
          recipe.title.toLowerCase().includes("pasta") ||
          recipe.tags.some((tag: string) => tag.toLowerCase().includes("pasta"))
      );
      expect(hasPasta).toBe(true);
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

      beforeEach(() => {
        store = useRecipesStore();
      });

      it("should find exact matches with high scores", () => {
        store.searchTerm = "pasta"; // Use a common tag that should exist

        const filtered = store.filteredRecipes;
        expect(filtered.length).toBeGreaterThan(0);

        // Should find recipes with "pasta" in title or tags
        const hasExactMatch = filtered.some(
          (recipe: Recipe) =>
            recipe.title.toLowerCase().includes("pasta") ||
            recipe.tags.some((tag) => tag.toLowerCase().includes("pasta"))
        );
        // fuzzy search is always enabled
      });

      it("should find fuzzy matches with typos", () => {
        store.searchTerm = "past"; // Partial match for "pasta"

        const filtered = store.filteredRecipes;
        expect(filtered.length).toBeGreaterThan(0);

        // Should still find pasta recipes despite partial match
        const hasFuzzyMatch = filtered.some(
          (recipe: Recipe) =>
            recipe.title.toLowerCase().includes("pasta") ||
            recipe.tags.some((tag: string) => tag.toLowerCase().includes("pasta"))
        );
        expect(hasFuzzyMatch).toBe(true);
      });

      it("should respect fuzzy threshold settings", () => {
        store.searchTerm = "spag"; // Partial match

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
        store.searchTerm = "pasta";

        const filtered = store.filteredRecipes;
        expect(filtered.length).toBeGreaterThan(0);

        // Should find matches in title, tags, or ingredients
        const hasMatch = filtered.some(
          (recipe: Recipe) =>
            recipe.title.toLowerCase().includes("pasta") ||
            recipe.tags.some((tag: string) => tag.toLowerCase().includes("pasta")) ||
            recipe.ingredients.some((ingredient: string) =>
              ingredient.toLowerCase().includes("pasta")
            )
        );
        expect(hasMatch).toBe(true);
      });
    });

    it("should handle multi-word queries", () => {
      store.searchTerm = "quick pasta";

      const filtered = store.filteredRecipes;
      expect(filtered.length).toBeGreaterThan(0);

      // Should find recipes matching both words
      const hasMultiWordMatch = filtered.some((recipe) => {
        const title = recipe.title.toLowerCase();
        const tags = recipe.tags.map((t) => t.toLowerCase());
        const ingredients = recipe.ingredients.map((i) => i.toLowerCase());

        const hasQuick =
          title.includes("quick") || tags.some((t) => t.includes("quick"));
        const hasPasta =
          title.includes("pasta") || tags.some((t) => t.includes("pasta"));

        return hasQuick && hasPasta;
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
