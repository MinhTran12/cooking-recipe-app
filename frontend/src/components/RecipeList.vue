<script setup>
import { useRecipesStore } from "../stores/recipes";
import { storeToRefs } from "pinia";
import { RouterLink } from "vue-router";
import { computed, ref } from "vue";

const store = useRecipesStore();
const { filteredRecipes, searchTerm } = storeToRefs(store);

const props = defineProps({
  filter: { type: String, default: "all" },
});

const displayedRecipes = computed(() => {
  if (props.filter === "favorite")
    return filteredRecipes.value.filter((r) => r.favorite);
  if (props.filter === "non-favorite")
    return filteredRecipes.value.filter((r) => !r.favorite);
  return filteredRecipes.value;
});

function handleTagClick(tag) {
  const terms = searchTerm.value.split(/\s+/).filter(Boolean);
  const i = terms.findIndex((t) => t.toLowerCase() === tag.toLowerCase());
  if (i !== -1) terms.splice(i, 1);
  else terms.push(tag);
  store.setSearchTerm(terms.join(" "));
}

const expanded = ref(new Set());
function toggleTags(id) {
  if (expanded.value.has(id)) expanded.value.delete(id);
  else expanded.value.add(id);
}
const isExpanded = (id) => expanded.value.has(id);

// compute visible/hidden tags for each recipe (cap shown tags unless expanded)
function tagsFor(r, cap = 6) {
  const tags = r.tags ?? [];
  const showAll = isExpanded(r.id);
  const visible = showAll ? tags : tags.slice(0, cap);
  const hiddenCount = Math.max(0, tags.length - visible.length);
  return { visible, hiddenCount };
}

const pageSize = 8;
const currentPage = ref(1);
const totalPages = computed(() =>
  Math.ceil(displayedRecipes.value.length / pageSize)
);
const paginatedRecipes = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return displayedRecipes.value.slice(start, start + pageSize);
});
</script>

<template>
  <div class="w-full">
    <p v-if="displayedRecipes.length === 0" class="text-center text-gray-500">
      No recipes found.
    </p>
    <div
      v-else
      class="mx-auto mt-6 w-full max-w-7xl px-4 grid gap-4 sm:gap-6 [grid-template-columns:repeat(auto-fill,minmax(16rem,1fr))]"
    >
      <div
        v-for="r in paginatedRecipes"
        :key="r.id"
        class="relative rounded-xl shadow-md border border-gray-200 overflow-hidden transition-transform duration-200 hover:scale-[1.02] w-full h-[20rem] flex flex-col cursor-pointer"
        style="background-color: #e7d3d3"
        @click="
          () => $router.push({ name: 'recipe-detail', params: { id: r.id } })
        "
      >
        <div class="flex items-center justify-center">
          <div
            class="w-full flex-none rounded-lg overflow-hidden bg-gray-200 h-28 sm:h-32 md:h-36"
          >
            <img
              v-if="r.image"
              :src="r.image"
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
        </div>

        <div class="px-4 pt-5">
          <div class="grid grid-cols-[1fr_auto] items-center gap-2">
            <span
              class="block text-lg font-semibold text-gray-800 truncate"
              :title="r.title"
            >
              {{ r.title }}
            </span>
            <button
              @click.stop="store.toggleFavorite(r.id)"
              class="text-2xl focus:outline-none w-9 h-9 flex items-center justify-center"
              :aria-label="
                r.favorite ? 'Unmark as favorite' : 'Mark as favorite'
              "
            >
              <span
                :class="[
                  r.favorite
                    ? 'text-yellow-500 group-hover:text-yellow-600'
                    : 'text-white group-hover:text-yellow-400',
                  'transition-colors duration-200',
                ]"
              >
                {{ r.favorite ? "★" : "☆" }}
              </span>
            </button>
          </div>
        </div>

        <div class="flex-1"></div>

        <div class="px-4">
          <span class="text-sm text-gray-500">{{ r.timeToPrepare }} min</span>
        </div>

        <div class="px-3 pb-3 pt-2">
          <div
            class="flex flex-wrap gap-1.5 items-center max-h-16 overflow-hidden"
            :class="isExpanded(r.id) ? 'max-h-24 overflow-y-auto pr-1' : ''"
          >
            <template v-for="t in tagsFor(r).visible" :key="t">
              <span
                class="text-xs rounded px-2 py-1 cursor-pointer whitespace-nowrap transition-colors border"
                :class="[
                  searchTerm
                    .split(/\s+/)
                    .map((s) => s.toLowerCase())
                    .includes(t.toLowerCase())
                    ? 'bg-[#B9375D] text-white border-[#B9375D]'
                    : 'bg-[#F5C9B0] text-[#B9375D] border-[#F5C9B0] hover:bg-[#B9375D] hover:text-white',
                ]"
                @click.stop="handleTagClick(t)"
                >#{{ t }}</span
              >
            </template>

            <button
              v-if="tagsFor(r).hiddenCount > 0 || isExpanded(r.id)"
              class="text-xs rounded px-2 py-1 border bg-gray-50 text-gray-700 hover:bg-gray-200"
              @click.stop="toggleTags(r.id)"
              :aria-expanded="isExpanded(r.id)"
            >
              <span v-if="!isExpanded(r.id)"
                >+{{ tagsFor(r).hiddenCount }} more</span
              >
              <span v-else>Show less</span>
            </button>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="totalPages > 1"
      class="flex justify-center items-center gap-2 mt-8"
    >
      <button
        @click="currentPage--"
        :disabled="currentPage === 1"
        class="px-3 py-1 rounded border bg-blue-100 text-blue-700 font-semibold disabled:opacity-50"
      >
        Prev
      </button>
      <span class="px-2">Page {{ currentPage }} of {{ totalPages }}</span>
      <button
        @click="currentPage++"
        :disabled="currentPage === totalPages"
        class="px-3 py-1 rounded border bg-blue-100 text-blue-700 font-semibold disabled:opacity-50"
      >
        Next
      </button>
    </div>
  </div>
</template>
