<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter, useRoute, RouterLink } from "vue-router";
import { useRecipesStore } from "@/stores/recipes";
import type { Recipe } from "@/types";

const route = useRoute();
const router = useRouter();
const store = useRecipesStore();

const recipe = computed((): Recipe | null =>
  store.getById(route.params.id as string)
);

function goBack(): void {
  router.push({ name: "recipes" });
}

const showConfirm = ref<boolean>(false);

function askDelete(): void {
  showConfirm.value = true;
}

function confirmDelete(): void {
  if (recipe.value) {
    store.deleteRecipe(recipe.value.id);
    router.push({ name: "recipes" });
  }
  showConfirm.value = false;
}

function cancelDelete(): void {
  showConfirm.value = false;
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
        @click="store.toggleFavorite(recipe.id)"
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
      <div v-if="!recipe" class="text-center text-gray-500">
        <p>Recipe not found.</p>
      </div>
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
            <strong>Time:</strong> {{ recipe.timeToPrepare }} min
          </div>
          <div class="bg-gray-100 rounded px-4 py-2 text-gray-700">
            <strong>Serving size:</strong> {{ recipe.servingSize }}
          </div>
          <div class="bg-gray-100 rounded px-4 py-2 text-gray-700">
            <strong>Calories:</strong> {{ recipe.caloriesPerServing }}
          </div>
        </div>

        <!-- Ingredients -->
        <h3 class="text-lg font-semibold mb-2 text-gray-700">Ingredients</h3>
        <ul class="mb-6 list-disc list-inside text-gray-600">
          <li v-for="(ing, i) in recipe.ingredients" :key="i">{{ ing }}</li>
        </ul>

        <!-- Instructions -->
        <h3 class="text-lg font-semibold mb-2 text-gray-700">Instructions</h3>
        <ol class="mb-6 list-decimal list-inside text-gray-600">
          <li v-for="(step, i) in recipe.instructions" :key="i">{{ step }}</li>
        </ol>

        <!-- Tags -->
        <h3 class="text-lg font-semibold mb-2 text-gray-700">Tags</h3>
        <div class="mb-6">
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
            <div class="flex gap-4 justify-center">
              <button
                @click="confirmDelete"
                class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition"
              >
                Delete
              </button>
              <button
                @click="cancelDelete"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition"
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
