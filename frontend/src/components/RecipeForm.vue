<script setup lang="ts">
import { reactive, watch } from "vue";
import type { Recipe, RecipeInput } from "@/types";

interface Props {
  modelValue?: Recipe | null;
  submitLabel?: string;
}

interface Emits {
  (e: "submit", payload: RecipeInput): void;
  (e: "update:modelValue", value: Recipe | null): void;
  (e: "cancel"): void;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  submitLabel: "Add",
});

const emit = defineEmits<Emits>();

const form = reactive({
  title: "",
  timeToPrepare: "",
  ingredientsInput: "",
  instructionsInput: "",
  tagsInput: "",
  caloriesPerServing: "",
  servingSize: "",
});

watch(
  () => props.modelValue,
  (r) => {
    if (!r) {
      form.title = "";
      form.timeToPrepare = "";
      form.ingredientsInput = "";
      form.instructionsInput = "";
      form.tagsInput = "";
      form.caloriesPerServing = "";
      form.servingSize = "";
      return;
    }
    form.title = r.title || "";
    form.timeToPrepare = String(r.timeToPrepare ?? "");
    form.ingredientsInput = (r.ingredients || []).join(", ");
    form.instructionsInput = (r.instructions || []).join("\n");
    form.tagsInput = (r.tags || []).join(", ");
    form.caloriesPerServing = String(r.caloriesPerServing ?? "");
    form.servingSize = String(r.servingSize ?? "");
  },
  { immediate: true }
);

function toList(input: string): string[] {
  return input
    .split(",")
    .map((s: string) => s.trim())
    .filter(Boolean);
}

function toSteps(input: string): string[] {
  return input
    .split("\n")
    .map((s: string) => s.trim())
    .filter(Boolean);
}

function onSubmit(): void {
  const payload: RecipeInput = {
    title: form.title || "Untitled Recipe",
    timeToPrepare: Number(form.timeToPrepare) || 0,
    ingredients: toList(form.ingredientsInput),
    instructions: toSteps(form.instructionsInput),
    tags: toList(form.tagsInput),
    caloriesPerServing: Number(form.caloriesPerServing) || 0,
    servingSize: Number(form.servingSize) || 0,
  };
  emit("submit", payload);
}
</script>

<template>
  <form @submit.prevent="onSubmit" class="space-y-6">
    <!-- Title -->
    <div>
      <label class="block text-gray-700 font-medium mb-1">Title</label>
      <input
        v-model="form.title"
        required
        class="w-full px-4 py-2 border border-black bg-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
      />
    </div>

    <!-- Time to prepare -->
    <div>
      <label class="block text-gray-700 font-medium mb-1"
        >Time to prepare (minutes)</label
      >
      <input
        type="number"
        min="0"
        v-model="form.timeToPrepare"
        required
        class="w-full px-4 py-2 border border-black bg-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
      />
    </div>

    <!-- Ingredients -->
    <div>
      <label class="block text-gray-700 font-medium mb-1"
        >Ingredients
        <span class="text-xs text-gray-400">(comma-separated)</span></label
      >
      <input
        v-model="form.ingredientsInput"
        placeholder="e.g. flour, eggs, milk"
        class="w-full px-4 py-2 border border-black bg-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
      />
    </div>

    <!-- Instructions -->
    <div>
      <label class="block text-gray-700 font-medium mb-1"
        >Instruction steps
        <span class="text-xs text-gray-400">(one per line)</span></label
      >
      <textarea
        v-model="form.instructionsInput"
        rows="6"
        placeholder="Step 1&#10;Step 2&#10;Step 3"
        class="w-full px-4 py-2 border border-black bg-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition resize-none"
      ></textarea>
    </div>

    <!-- Tags -->
    <div>
      <label class="block text-gray-700 font-medium mb-1"
        >Tags
        <span class="text-xs text-gray-400">(comma-separated)</span></label
      >
      <input
        v-model="form.tagsInput"
        placeholder="e.g. dessert, quick"
        class="w-full px-4 py-2 border border-black bg-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
      />
    </div>

    <!-- Calories per serving -->
    <div>
      <label class="block text-gray-700 font-medium mb-1"
        >Calories per serving</label
      >
      <input
        type="number"
        min="0"
        v-model="form.caloriesPerServing"
        class="w-full px-4 py-2 border border-black bg-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
      />
    </div>

    <!-- Serving size -->
    <div>
      <label class="block text-gray-700 font-medium mb-1">Serving size</label>
      <input
        type="number"
        min="0"
        v-model="form.servingSize"
        class="w-full px-4 py-2 border border-black bg-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
      />
    </div>

    <!-- Action buttons -->
    <div class="flex gap-4 justify-end">
      <button
        type="submit"
        class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
      >
        {{ submitLabel }}
      </button>
      <button
        type="button"
        @click="$emit('cancel')"
        class="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
      >
        Cancel
      </button>
    </div>
  </form>
</template>
