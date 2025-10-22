import { createRouter, createWebHistory } from "vue-router";

import RecipesPage from "@/pages/RecipesPage.vue";
import RecipeDetailPage from "@/pages/RecipeDetailPage.vue";
import RecipeEditPage from "@/pages/RecipeEditPage.vue";
import AddRecipePage from "@/pages/AddRecipePage.vue";

const routes = [
  { path: "/", redirect: "/recipes" }, // default redirect
  { path: "/recipes", name: "recipes", component: RecipesPage },
  {
    path: "/recipes/:id",
    name: "recipe-detail",
    component: RecipeDetailPage,
    props: true,
  },
  {
    path: "/recipes/:id/edit",
    name: "recipe-edit",
    component: RecipeEditPage,
    props: true,
  },
  { path: "/add", name: "add-recipe", component: AddRecipePage },
  { path: "/:pathMatch(.*)*", redirect: "/recipes" }, // catch-all
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
