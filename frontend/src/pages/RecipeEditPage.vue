<script setup lang="ts">
import { computed } from "vue";
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

function onSubmit(payload: RecipeInput): void {
  if (!recipe.value) return;
  store.updateRecipe(recipe.value.id, payload);
  router.push({ name: "recipe-detail", params: { id: recipe.value.id } });
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
      <div v-if="!recipe" class="text-center text-gray-500">
        <p>Recipe not found.</p>
      </div>
      <div v-else>
        <RecipeForm
          :modelValue="recipe"
          submitLabel="Save"
          @submit="onSubmit"
          @cancel="onCancel"
        />
      </div>
    </div>
  </div>
</template>
