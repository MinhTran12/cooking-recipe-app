-- Recipe Manager Database Schema
-- Based on the frontend Recipe interface

-- Create the recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    image VARCHAR(500),
    ingredients TEXT[] NOT NULL,
    instructions TEXT[] NOT NULL,
    time_to_prepare INTEGER NOT NULL CHECK (time_to_prepare > 0),
    tags TEXT[] DEFAULT '{}',
    calories_per_serving INTEGER NOT NULL CHECK (calories_per_serving > 0),
    serving_size INTEGER NOT NULL CHECK (serving_size > 0),
    favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on title for faster searches
CREATE INDEX IF NOT EXISTS idx_recipes_title ON recipes(title);

-- Create an index on tags for faster tag-based searches
CREATE INDEX IF NOT EXISTS idx_recipes_tags ON recipes USING GIN(tags);

-- Create an index on favorite for faster filtering
CREATE INDEX IF NOT EXISTS idx_recipes_favorite ON recipes(favorite);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create a trigger to automatically update the updated_at column
CREATE TRIGGER update_recipes_updated_at 
    BEFORE UPDATE ON recipes 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create a view for easier querying (optional)
CREATE VIEW recipe_summary AS
SELECT 
    id,
    title,
    time_to_prepare,
    array_length(ingredients, 1) as ingredient_count,
    calories_per_serving,
    serving_size,
    favorite,
    tags
FROM recipes
ORDER BY created_at DESC;

-- Note: Sample data is inserted via seed_database.py script
-- Run: python backend/db/seed_database.py