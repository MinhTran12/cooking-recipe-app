<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useRecipesStore } from "@/stores/recipes";
import RecipeForm from "@/components/RecipeForm.vue";
import type { RecipeInput } from "@/types";

const router = useRouter();
const store = useRecipesStore();
const isSubmitting = ref(false);
const submitError = ref<string | null>(null);

async function onSubmit(payload: RecipeInput): Promise<void> {
  isSubmitting.value = true;
  submitError.value = null;

  try {
    const recipeId = await store.addRecipe(payload);
    router.push({ name: "recipe-detail", params: { id: recipeId } });
  } catch (error) {
    submitError.value =
      error instanceof Error ? error.message : "Failed to add recipe";
  } finally {
    isSubmitting.value = false;
  }
}

function onCancel(): void {
  router.push({ name: "recipes" });
}
</script>

<template>
  <div class="flex flex-col items-center justify-start min-h-screen py-8">
    <div
      class="w-full max-w-xl rounded-xl shadow-md p-8"
      style="background-color: #e7d3d3"
    >
      <h2 class="text-2xl font-bold mb-6 text-gray-800 text-center">
        Add Recipe
      </h2>

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

      <!-- Loading state -->
      <div v-if="isSubmitting" class="mb-4 text-center">
        <div
          class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900"
        ></div>
        <span class="ml-2">Adding recipe...</span>
      </div>

      <RecipeForm
        submitLabel="Add"
        :disabled="isSubmitting"
        @submit="onSubmit"
        @cancel="onCancel"
      />
    </div>
  </div>
</template>
