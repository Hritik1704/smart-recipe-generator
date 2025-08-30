import React, { useState } from 'react';
import { ChefHat, Utensils, Clock, Users, AlertCircle } from 'lucide-react';
import './App.css';

const GEMINI_API_KEY = 'AIzaSyCbc1bzqKN465PKgV5TUCs4JK5HdFm6hYw';
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

function App() {
  const [ingredients, setIngredients] = useState('');
  const [preferences, setPreferences] = useState('');
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateRecipe = async () => {
    if (!ingredients.trim()) {
      setError('Please enter some ingredients');
      return;
    }

    setLoading(true);
    setError('');
    setRecipe(null);

    try {
      const prompt = `Create a detailed recipe using these ingredients: ${ingredients}. 
      ${preferences ? `Additional preferences: ${preferences}` : ''}
      
      Please provide the response in this exact JSON format:
      {
        "name": "Recipe Name",
        "description": "Brief description",
        "cookingTime": "X minutes",
        "servings": "X people",
        "difficulty": "Easy/Medium/Hard",
        "ingredients": ["ingredient 1", "ingredient 2"],
        "instructions": ["step 1", "step 2", "step 3"],
        "tips": "Helpful cooking tips"
      }`;

      const response = await fetch(GEMINI_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-goog-api-key': GEMINI_API_KEY,
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: prompt
            }]
          }]
        })
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      const generatedText = data.candidates?.[0]?.content?.parts?.[0]?.text;

      if (!generatedText) {
        throw new Error('No recipe generated');
      }

      // Extract JSON from the response
      const jsonMatch = generatedText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const recipeData = JSON.parse(jsonMatch[0]);
        setRecipe(recipeData);
      } else {
        // Fallback: parse the text manually
        setRecipe({
          name: "Generated Recipe",
          description: "AI-generated recipe based on your ingredients",
          cookingTime: "30 minutes",
          servings: "4 people",
          difficulty: "Medium",
          ingredients: ingredients.split(',').map(i => i.trim()),
          instructions: generatedText.split('\n').filter(line => line.trim()),
          tips: "Enjoy your cooking!"
        });
      }
    } catch (err) {
      console.error('Error generating recipe:', err);
      setError('Failed to generate recipe. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearRecipe = () => {
    setRecipe(null);
    setIngredients('');
    setPreferences('');
    setError('');
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div className="header-content">
            <ChefHat size={40} className="header-icon" />
            <div>
              <h1 className="header-title">Smart Recipe Generator</h1>
              <p className="header-subtitle">AI-powered recipes using Google Gemini</p>
            </div>
          </div>
        </header>

        <div className="main-content">
          <div className="input-section card">
            <h2 className="section-title">
              <Utensils size={24} />
              What ingredients do you have?
            </h2>
            
            <div className="form-group">
              <label htmlFor="ingredients">Ingredients (comma-separated)</label>
              <textarea
                id="ingredients"
                className="textarea"
                value={ingredients}
                onChange={(e) => setIngredients(e.target.value)}
                placeholder="e.g., chicken, tomatoes, onions, garlic, rice..."
                rows={3}
              />
            </div>

            <div className="form-group">
              <label htmlFor="preferences">Dietary preferences or cuisine type (optional)</label>
              <input
                id="preferences"
                type="text"
                className="input"
                value={preferences}
                onChange={(e) => setPreferences(e.target.value)}
                placeholder="e.g., vegetarian, Italian, spicy, low-carb..."
              />
            </div>

            {error && (
              <div className="error">
                <AlertCircle size={20} />
                {error}
              </div>
            )}

            <div className="button-group">
              <button
                className="btn btn-primary"
                onClick={generateRecipe}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <div className="loading"></div>
                    Generating Recipe...
                  </>
                ) : (
                  <>
                    <ChefHat size={20} />
                    Generate Recipe
                  </>
                )}
              </button>

              {recipe && (
                <button
                  className="btn btn-secondary"
                  onClick={clearRecipe}
                >
                  New Recipe
                </button>
              )}
            </div>
          </div>

          {recipe && (
            <div className="recipe-section">
              <div className="recipe-card card">
                <h2 className="recipe-title">{recipe.name}</h2>
                
                <div className="recipe-meta">
                  <div className="meta-item">
                    <Clock size={18} />
                    <span>{recipe.cookingTime}</span>
                  </div>
                  <div className="meta-item">
                    <Users size={18} />
                    <span>{recipe.servings}</span>
                  </div>
                  <div className="meta-item">
                    <span className={`difficulty ${recipe.difficulty?.toLowerCase()}`}>
                      {recipe.difficulty}
                    </span>
                  </div>
                </div>

                {recipe.description && (
                  <div className="recipe-description">
                    <p>{recipe.description}</p>
                  </div>
                )}

                <div className="recipe-content">
                  <div className="ingredients-section">
                    <h3>Ingredients</h3>
                    <ul>
                      {recipe.ingredients?.map((ingredient, index) => (
                        <li key={index}>{ingredient}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="instructions-section">
                    <h3>Instructions</h3>
                    <ol>
                      {recipe.instructions?.map((step, index) => (
                        <li key={index}>{step}</li>
                      ))}
                    </ol>
                  </div>

                  {recipe.tips && (
                    <div className="tips-section">
                      <h3>Tips</h3>
                      <p>{recipe.tips}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        <footer className="footer">
          <p>Powered by Google Gemini AI • Smart Recipe Generator</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
