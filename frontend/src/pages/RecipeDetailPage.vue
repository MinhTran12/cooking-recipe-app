<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { useRouter, useRoute, RouterLink } from "vue-router";
import { useRecipesStore } from "@/stores/recipes";
import type { Recipe } from "@/types";

const route = useRoute();
const router = useRouter();
const store = useRecipesStore();

const recipe = computed((): Recipe | null =>
  store.getById(route.params.id as string)
);

const deleteLoading = ref(false);
const deleteError = ref<string | null>(null);

// Load recipes if not already loaded
onMounted(() => {
  if (store.recipes.length === 0) {
    store.loadRecipes();
  }
});

function goBack(): void {
  router.push({ name: "recipes" });
}

const showConfirm = ref<boolean>(false);

function askDelete(): void {
  showConfirm.value = true;
  deleteError.value = null;
}

async function confirmDelete(): Promise<void> {
  if (recipe.value) {
    deleteLoading.value = true;
    deleteError.value = null;
    try {
      await store.deleteRecipe(recipe.value.id);
      router.push({ name: "recipes" });
    } catch (error) {
      deleteError.value =
        error instanceof Error ? error.message : "Failed to delete recipe";
    } finally {
      deleteLoading.value = false;
    }
  }
  showConfirm.value = false;
}

function cancelDelete(): void {
  showConfirm.value = false;
  deleteError.value = null;
}

async function toggleFavorite(): Promise<void> {
  if (recipe.value) {
    try {
      await store.toggleFavorite(recipe.value.id);
    } catch (error) {
      console.error("Failed to toggle favorite:", error);
    }
  }
}
</script>

<template>
  <div class="flex flex-col items-center justify-start min-h-screen py-8">
    <div
      class="w-full max-w-xl rounded-xl shadow-md p-8 relative"
      style="background-color: #e7d3d3"
    >
      <button
        @click="goBack"
        class="mb-4 px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition"
      >
        ← Back
      </button>
      <button
        v-if="recipe"
        @click="toggleFavorite"
        class="absolute top-6 right-4 text-2xl focus:outline-none group transition-colors duration-200 z-10"
        :aria-label="
          recipe.favorite ? 'Unmark as favorite' : 'Mark as favorite'
        "
        style="background: none; border: none"
      >
        <span
          :class="[
            recipe.favorite
              ? 'text-yellow-500 group-hover:text-yellow-400'
              : 'text-white group-hover:text-yellow-300',
            'transition-colors duration-200 text-4xl',
          ]"
        >
          {{ recipe.favorite ? "★" : "☆" }}
        </span>
      </button>

      <!-- Loading state -->
      <div v-if="store.loading" class="text-center text-gray-500">
        <div
          class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mb-2"
        ></div>
        <p>Loading recipe...</p>
      </div>

      <!-- Recipe not found -->
      <div v-else-if="!recipe" class="text-center text-gray-500">
        <p>Recipe not found.</p>
      </div>

      <!-- Recipe content -->
      <div v-else>
        <div class="flex flex-col items-center mb-4">
          <div
            class="w-full flex-none rounded-lg overflow-hidden bg-gray-200 h-48 mb-4"
          >
            <img
              v-if="recipe.image"
              :src="recipe.image"
              alt="Recipe image"
              class="object-cover w-full h-full"
            />
            <img
              v-else
              src="/src/public/bunch-of-food.jpg"
              alt="Default food"
              class="object-cover w-full h-full"
            />
          </div>
          <h2 class="text-2xl font-bold text-gray-800 text-center">
            {{ recipe.title }}
          </h2>
        </div>

        <!-- Basic Info -->
        <div class="flex flex-wrap justify-center gap-4 mb-6">
          <div class="bg-gray-100 rounded px-4 py-2 text-gray-700">
            <strong>Time:</strong> {{ recipe.timeToPrepare || "Not specified" }}
            <span v-if="recipe.timeToPrepare">min</span>
          </div>
          <div class="bg-gray-100 rounded px-4 py-2 text-gray-700">
            <strong>Serving size:</strong>
            {{ recipe.servingSize || "Not specified" }}
          </div>
          <div class="bg-gray-100 rounded px-4 py-2 text-gray-700">
            <strong>Calories:</strong>
            {{ recipe.caloriesPerServing || "Not specified" }}
          </div>
        </div>

        <!-- Ingredients -->
        <div class="mb-6">
          <h3 class="text-lg font-semibold mb-2 text-gray-700">Ingredients</h3>
          <ul
            v-if="recipe.ingredients && recipe.ingredients.length > 0"
            class="list-disc list-inside text-gray-600"
          >
            <li v-for="(ing, i) in recipe.ingredients" :key="i">{{ ing }}</li>
          </ul>
          <p v-else class="text-gray-500 italic">No ingredients added yet.</p>
        </div>

        <!-- Instructions -->
        <div class="mb-6">
          <h3 class="text-lg font-semibold mb-2 text-gray-700">Instructions</h3>
          <ol
            v-if="recipe.instructions && recipe.instructions.length > 0"
            class="list-decimal list-inside text-gray-600"
          >
            <li v-for="(step, i) in recipe.instructions" :key="i">
              {{ step }}
            </li>
          </ol>
          <p v-else class="text-gray-500 italic">No instructions added yet.</p>
        </div>

        <!-- Tags -->
        <div class="mb-6">
          <h3 class="text-lg font-semibold mb-2 text-gray-700">Tags</h3>
          <div v-if="recipe.tags && recipe.tags.length > 0">
            <span
              v-for="t in recipe.tags"
              :key="t"
              class="inline-block text-xs rounded px-2 py-1 mr-1 mb-1 border cursor-default"
              :style="{
                backgroundColor: '#F5C9B0',
                color: '#B9375D',
                borderColor: '#F5C9B0',
              }"
              >#{{ t }}</span
            >
          </div>
          <p v-else class="text-gray-500 italic">No tags added yet.</p>
        </div>

        <div class="flex gap-4">
          <RouterLink
            :to="{ name: 'recipe-edit', params: { id: recipe.id } }"
            class="flex-1 inline-flex justify-center px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
          >
            Edit
          </RouterLink>

          <button
            @click="askDelete"
            class="flex-1 inline-flex justify-center px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition"
          >
            Delete
          </button>
        </div>

        <!-- Confirmation modal -->
        <div
          v-if="showConfirm"
          class="fixed inset-0 flex items-center justify-center backdrop-blur-sm z-50"
        >
          <div
            class="rounded-xl shadow-lg p-6 w-full max-w-xs text-center"
            style="background-color: #e7d3d3"
          >
            <p class="mb-4 text-gray-800">
              Are you sure you want to delete this recipe?
            </p>

            <!-- Delete error -->
            <div
              v-if="deleteError"
              class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm"
            >
              {{ deleteError }}
            </div>

            <div class="flex gap-4 justify-center">
              <button
                @click="confirmDelete"
                :disabled="deleteLoading"
                class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition disabled:opacity-50"
              >
                <span v-if="deleteLoading">Deleting...</span>
                <span v-else>Delete</span>
              </button>
              <button
                @click="cancelDelete"
                :disabled="deleteLoading"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
