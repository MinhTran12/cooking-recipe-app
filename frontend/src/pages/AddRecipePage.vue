<script setup lang="ts">
import { useRouter } from "vue-router";
import { useRecipesStore } from "@/stores/recipes";
import RecipeForm from "@/components/RecipeForm.vue";
import type { RecipeInput } from "@/types";

const router = useRouter();
const store = useRecipesStore();

function onSubmit(payload: RecipeInput): void {
  const id = store.addRecipe(payload);
  router.push({ name: "recipe-detail", params: { id } });
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
      <RecipeForm submitLabel="Add" @submit="onSubmit" @cancel="onCancel" />
    </div>
  </div>
</template>
