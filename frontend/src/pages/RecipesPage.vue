<script setup>
import SearchBar from "../components/SearchBar.vue";
import RecipeList from "../components/RecipeList.vue";
import { RouterLink } from "vue-router";
import { ref } from "vue";

const filter = ref("all");
</script>

<template>
  <div class="flex flex-col items-center justify-start min-h-screen py-8">
    <h1 class="text-3xl font-bold mb-8 text-gray-800 px-4 font-story-script">
      Cooking Recipe Manager
    </h1>
    <div
      class="mb-6 w-full max-w-2xl flex flex-col sm:flex-row items-center gap-4 px-4"
    >
      <SearchBar />
      <div class="pb-10 w-full sm:w-auto mb-14">
        <select
          id="filter-select"
          v-model="filter"
          class="px-5 py-3 border-2 border-blue-400 rounded-xl shadow focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg transition w-full sm:w-auto"
        >
          <option value="all">All</option>
          <option value="favorite">Favorite</option>
          <option value="non-favorite">Non-Favorite</option>
        </select>
      </div>
    </div>
    <div class="mb-6">
      <RouterLink
        :to="{ name: 'add-recipe' }"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
        >+ Add Recipe</RouterLink
      >
    </div>
    <RecipeList :filter="filter" />
  </div>
</template>
