<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useRecipesStore } from "@/stores/recipes";
import RecipeForm from "@/components/RecipeForm.vue";
import type { Recipe, RecipeInput } from "@/types";

const route = useRoute();
const router = useRouter();
const store = useRecipesStore();

const recipe = computed((): Recipe | null =>
  store.getById(route.params.id as string)
);

const isSubmitting = ref(false);
const submitError = ref<string | null>(null);

// Load recipes if not already loaded
onMounted(() => {
  if (store.recipes.length === 0) {
    store.loadRecipes();
  }
});

async function onSubmit(payload: RecipeInput): Promise<void> {
  if (!recipe.value) return;

  isSubmitting.value = true;
  submitError.value = null;

  try {
    await store.updateRecipe(recipe.value.id, payload);
    router.push({ name: "recipe-detail", params: { id: recipe.value.id } });
  } catch (error) {
    submitError.value =
      error instanceof Error ? error.message : "Failed to update recipe";
  } finally {
    isSubmitting.value = false;
  }
}

function onCancel(): void {
  if (recipe.value) {
    router.push({ name: "recipe-detail", params: { id: recipe.value.id } });
  } else {
    router.push({ name: "recipes" });
  }
}
</script>

<template>
  <div class="flex flex-col items-center justify-start min-h-screen py-8">
    <div
      class="w-full max-w-xl rounded-xl shadow-md p-8"
      style="background-color: #e7d3d3"
    >
      <h2 class="text-2xl font-bold mb-6 text-gray-800 text-center">
        Edit Recipe
      </h2>

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

      <!-- Recipe form -->
      <div v-else>
        <!-- Error message -->
        <div
          v-if="submitError"
          class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded"
        >
          {{ submitError }}
          <button
            @click="submitError = null"
            class="float-right text-red-700 hover:text-red-900"
          >
            ×
          </button>
        </div>

        <!-- Submitting state -->
        <div v-if="isSubmitting" class="mb-4 text-center">
          <div
            class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"
          ></div>
          <span class="ml-2">Updating recipe...</span>
        </div>

        <RecipeForm
          :modelValue="recipe"
          submitLabel="Save"
          :disabled="isSubmitting"
          @submit="onSubmit"
          @cancel="onCancel"
        />
      </div>
    </div>
  </div>
</template>
