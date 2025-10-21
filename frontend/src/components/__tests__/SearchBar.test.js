import { describe, it, expect, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import SearchBar from "../SearchBar.vue";
import { useRecipesStore } from "../../stores/recipes";

describe("SearchBar Component", () => {
  let wrapper;
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useRecipesStore();

    wrapper = mount(SearchBar, {
      global: {
        plugins: [createPinia()],
      },
    });
  });

  describe("Rendering", () => {
    it("should render search input", () => {
      const input = wrapper.find('input[placeholder*="Search by name"]');
      expect(input.exists()).toBe(true);
      expect(input.attributes("placeholder")).toBe(
        "Search by name, tag, or ingredient..."
      );
    });

    it("should render search logic button", () => {
      const button = wrapper.find("button");
      expect(button.exists()).toBe(true);
      expect(button.text()).toContain("AND");
    });

    it("should render sensitivity slider when fuzzy search is enabled", () => {
      const slider = wrapper.find('input[type="range"]');
      expect(slider.exists()).toBe(true);
    });
  });

  describe("User Interactions", () => {
    it("should have input field that accepts text", async () => {
      const input = wrapper.find('input[placeholder*="Search by name"]');
      await input.setValue("pasta");

      // Check that the input value was set
      expect(input.element.value).toBe("pasta");
    });

    it("should have button that can be clicked", async () => {
      const button = wrapper.find("button");

      // Just verify the button exists and can be clicked
      expect(button.exists()).toBe(true);
      await button.trigger("click");
      // Button click should not throw an error
    });

    it("should have slider that can be adjusted", async () => {
      const slider = wrapper.find('input[type="range"]');

      await slider.setValue(50);

      expect(slider.element.value).toBe("50");
    });
  });

  describe("Display Logic", () => {
    it("should show current search logic in button", () => {
      const button = wrapper.find("button");
      expect(button.text()).toContain(store.searchLogic);
    });

    it("should show sensitivity slider", () => {
      const slider = wrapper.find('input[type="range"]');
      expect(slider.exists()).toBe(true);
    });

    it("should display current fuzzy threshold value", () => {
      const thresholdDisplay = wrapper.find("span.fuzzy.w-6");
      expect(thresholdDisplay.text()).toContain(
        store.fuzzyThreshold.toString()
      );
    });
  });

  describe("Accessibility", () => {
    it("should have proper aria-label on search input", () => {
      const input = wrapper.find('input[placeholder*="Search by name"]');
      expect(input.attributes("aria-label")).toBe("Search recipes");
    });

    it("should have proper aria-label on logic button", () => {
      const button = wrapper.find("button");
      expect(button.attributes("aria-label")).toBe("Toggle search logic");
    });
  });
});
