<script setup lang="ts">
import { storeToRefs } from "pinia";
import { useRecipesStore } from "@/stores/recipes";

const store = useRecipesStore();
const { searchTerm, searchLogic, fuzzyThreshold } = storeToRefs(store);

const toggleLogic = (): void => {
  store.setSearchLogic(searchLogic.value === "AND" ? "OR" : "AND");
};

const updateThreshold = (event: Event): void => {
  const target = event.target as HTMLInputElement;
  store.setFuzzyThreshold(parseInt(target.value));
};
</script>

<template>
  <div class="flex flex-col items-center w-full gap-3">
    <input
      v-model="searchTerm"
      placeholder="Search by name and tag..."
      aria-label="Search recipes"
      class="w-full max-w-xl px-5 py-3 border-2 border-blue-400 rounded-xl shadow focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg transition"
    />

    <div class="flex items-center gap-2 mt-2">
      <span class="text-gray-600">Logic:</span>
      <button
        @click="toggleLogic"
        class="px-3 py-1 rounded bg-blue-100 text-blue-700 font-semibold border border-blue-300 hover:bg-blue-200 transition"
        aria-label="Toggle search logic"
      >
        {{ searchLogic }}
      </button>
      <span class="text-sm text-gray-400"
        >(AND: all words must match, OR: any word matches)</span
      >
    </div>

    <div class="flex items-center gap-2 mt-2">
      <span class="text-gray-600">Fuzzy search sensitivity:</span>
      <span class="text-gray-400">Loose</span>
      <input
        type="range"
        min="0"
        max="100"
        :value="fuzzyThreshold"
        @input="updateThreshold"
        class="w-25 h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer"
      />
      <span class="fuzzy w-6">{{ fuzzyThreshold }}</span>
      <span class="text-gray-400">Strict</span>
    </div>
  </div>
</template>
