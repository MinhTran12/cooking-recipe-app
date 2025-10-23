import { defineStore } from "pinia";
import mockRecipes from "@/stores/mockRecipes.json";
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
    for (const tag of recipe.tags) {
      const tagMatch = fuzzyMatch(tag, word);
      if (tagMatch.matched) {
        bestScore = Math.max(bestScore, tagMatch.score);
        wordMatched = true;
      }
    }

    // Check ingredients
    for (const ingredient of recipe.ingredients) {
      const ingredientMatch = fuzzyMatch(ingredient, word);
      if (ingredientMatch.matched) {
        bestScore = Math.max(bestScore, ingredientMatch.score * 0.8); // Ingredients get lower weight
        wordMatched = true;
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

// Pinia store for managing recipes and mocking API interactions
export const useRecipesStore = defineStore("recipes", {
  state: (): RecipesState => ({
    recipes: mockRecipes as Recipe[],
    searchTerm: "",
    searchLogic: "AND" as SearchLogic,
    fuzzyThreshold: 100,
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

    addRecipe(partial: RecipeInput): string {
      const recipe: Recipe = {
        id: (Date.now() + Math.random()).toString(36),
        image: partial.image || "",
        title: partial.title?.trim() || "Untitled Recipe",
        ingredients: Array.isArray(partial.ingredients)
          ? partial.ingredients
          : [],
        // ensure array of non-empty strings
        instructions: Array.isArray(partial.instructions)
          ? partial.instructions.filter(Boolean)
          : [],
        timeToPrepare: Number(partial.timeToPrepare) || 0,
        tags: Array.isArray(partial.tags) ? partial.tags : [],
        caloriesPerServing: Number(partial.caloriesPerServing) || 0,
        servingSize: Number(partial.servingSize) || 0,
        favorite: partial.favorite || false,
      };
      this.recipes.unshift(recipe);
      return recipe.id;
    },

    deleteRecipe(id: string): void {
      const i = this.recipes.findIndex((r) => r.id === id);
      if (i !== -1) this.recipes.splice(i, 1);
    },

    updateRecipe(id: string, patch: Partial<RecipeInput>): void {
      const i = this.recipes.findIndex((r) => r.id === id);
      if (i === -1) return;
      const normalized = {
        ...patch,
        title: typeof patch.title === "string" ? patch.title.trim() : undefined,
        timeToPrepare:
          patch.timeToPrepare != null ? Number(patch.timeToPrepare) : undefined,
        caloriesPerServing:
          patch.caloriesPerServing != null
            ? Number(patch.caloriesPerServing)
            : undefined,
        servingSize:
          patch.servingSize != null ? Number(patch.servingSize) : undefined,
        // if provided, keep instructions as string[]
        instructions: Array.isArray(patch.instructions)
          ? patch.instructions.filter(Boolean)
          : undefined,
      };
      // Filter out undefined values and update recipe
      const filteredUpdate = Object.fromEntries(
        Object.entries(normalized).filter(([_, value]) => value !== undefined)
      ) as Partial<Recipe>;
      this.recipes[i] = { ...this.recipes[i], ...filteredUpdate };
    },

    toggleFavorite(id: string): void {
      const i = this.recipes.findIndex((r) => r.id === id);
      if (i === -1) return;
      this.recipes[i].favorite = !this.recipes[i].favorite;
    },
  },
});
