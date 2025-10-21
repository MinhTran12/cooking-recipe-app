# Cooking Recipe Manager

This is a cooking recipe manager front end application built with Vue 3 + Vite + Tailwind.

[![Recipe Manager UI](recipe-manager-ui.png)](recipe-manager-ui.png)


## Features

- Clean preview of different recipes in card forms, and to see the details upon selection
- Add new recipes, edit or delete existing ones, and tag favorite recipes
- Fuzzy search and AND/OR logic for filtering based on favorite recipes, and recipe names and tags
- Pinia state management
- Unit and component tests with Vitest and Vue Test Utils

## Recipe Data Structure

A recipe object contains the following fields:

```json
{
   "id": "string",
   "title": "string",
   "image": "string",
   "timeToPrepare": 30,
   "ingredients": ["string"],
   "instructions": ["string"],
   "tags": ["string"],
   "caloriesPerServing": 250,
   "servingSize": 4,
   "favorite": false
}
```

## Prerequisites

- Node.js (v16 or higher recommended)
- npm (comes with Node.js)

## Getting Started

### 1. Clone the repository

```sh
git clone https://github.com/MinhTran12/recipe-manager-front-end.git
cd recipe-manager-front-end
```

### 2. Install front end Dependencies

```sh
cd frontend
npm install
```

### 3. Run the front end

```sh
npm run dev
```

## Testing

Navigate to the front end directory and run:

### Test for development purpose
```sh
npm run test
```
### Run tests once
```sh
npm run test:run
```

### Run tests with interactive UI
```sh
npm run test:ui
```

### Run tests with coverage report
```sh
npm run test:coverage
```

The two test files are placed in store or component files, inside the `__tests__` folder within the `src` directory. The tests cover search logic, CRUD and component behavior, and rendering.

## Documentation

- [Vue 3 Documentation](https://vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Pinia (State Management)](https://pinia.vuejs.org/)
- [Tailwind Documentation](https://tailwindcss.com/docs)

---
