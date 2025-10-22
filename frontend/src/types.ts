// Core Recipe interface based on the mockRecipes.json structure
export interface Recipe {
  id: string
  title: string
  image?: string
  ingredients: string[]
  instructions: string[]
  timeToPrepare: number
  tags: string[]
  caloriesPerServing: number
  servingSize: number
  favorite: boolean
}

// Partial recipe for creating/updating recipes
export type RecipeInput = Omit<Recipe, 'id' | 'favorite'> & {
  id?: string
  favorite?: boolean
}

// Recipe form data structure
export interface RecipeFormData {
  title: string
  timeToPrepare: string | number
  ingredientsInput: string
  instructionsInput: string
  tagsInput: string
  caloriesPerServing: string | number
  servingSize: string | number
}

// Search logic types
export type SearchLogic = 'AND' | 'OR'

// Fuzzy search result
export interface FuzzyMatchResult {
  score: number
  matched: boolean
}

// Store state interface for Pinia
export interface RecipesState {
  recipes: Recipe[]
  searchTerm: string
  searchLogic: SearchLogic
  fuzzyThreshold: number
}

// Router param types
export interface RouteParams {
  id: string
}

// Component emit types
export interface RecipeFormEmits {
  submit: [payload: RecipeInput]
  cancel: []
  'update:modelValue': [value: Recipe | null]
}

// Component props types
export interface RecipeFormProps {
  modelValue?: Recipe | null
  submitLabel?: string
}

export interface SearchBarEmits {
  'update:searchTerm': [value: string]
  'update:searchLogic': [value: SearchLogic]
  'update:fuzzyThreshold': [value: number]
}

export interface SearchBarProps {
  searchTerm: string
  searchLogic: SearchLogic
  fuzzyThreshold: number
}