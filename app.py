"""
Smart Recipe Generator - Technical Assessment Project
A comprehensive recipe suggestion application with ML-powered recommendations.
"""

import os
import json
import logging
import random
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'smart-recipe-generator-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Load recipe database
def load_recipe_database():
    """Load recipes from JSON file"""
    try:
        with open('data/recipes.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Recipe database not found, using default recipes")
        return []

class IngredientDetector:
    """Mock ingredient detection from images"""
    
    def __init__(self):
        self.available_ingredients = [
            'apple', 'avocado', 'bacon', 'banana', 'basil', 'beef', 'bell pepper', 'black pepper',
            'broccoli', 'butter', 'carrot', 'cheese', 'chicken breast', 'chickpeas', 'cilantro',
            'cucumber', 'dill', 'eggs', 'garlic', 'ginger', 'ground beef', 'lemon', 'lettuce',
            'lime', 'mushroom', 'olive oil', 'onion', 'parmesan cheese', 'quinoa', 'rice',
            'salmon fillet', 'soy sauce', 'spaghetti', 'spinach', 'taco shells', 'tahini',
            'tomato', 'asparagus', 'flour', 'sugar', 'coconut milk', 'fish sauce', 'shrimp',
            'tofu', 'noodles', 'potatoes', 'cod', 'yogurt', 'cream', 'wine', 'herbs'
        ]
    
    def detect_ingredients(self, image_path):
        """Mock ingredient detection - returns random ingredients for demo"""
        num_ingredients = random.randint(3, 8)
        detected = random.sample(self.available_ingredients, num_ingredients)
        confidence_scores = [round(random.uniform(0.7, 0.95), 2) for _ in detected]
        
        return {
            'ingredients': detected,
            'confidence_scores': confidence_scores,
            'total_detected': len(detected)
        }

class RecipeRecommendationEngine:
    """Advanced ML-powered recipe recommendation system"""
    
    def __init__(self, recipes):
        self.recipes = recipes
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.recipe_vectors = None
        self.ingredient_substitutions = self._load_substitutions()
        if recipes:
            self._prepare_vectors()
    
    def _load_substitutions(self):
        """Load ingredient substitution mappings"""
        return {
            'butter': ['olive oil', 'coconut oil', 'margarine'],
            'milk': ['almond milk', 'soy milk', 'coconut milk'],
            'eggs': ['flax eggs', 'chia eggs', 'applesauce'],
            'flour': ['almond flour', 'coconut flour', 'oat flour'],
            'sugar': ['honey', 'maple syrup', 'stevia'],
            'chicken': ['tofu', 'tempeh', 'mushrooms'],
            'beef': ['lentils', 'black beans', 'portobello mushrooms'],
            'cheese': ['nutritional yeast', 'cashew cheese', 'vegan cheese'],
            'cream': ['coconut cream', 'cashew cream', 'silken tofu'],
            'bacon': ['tempeh bacon', 'coconut bacon', 'mushroom bacon']
        }
    
    def _prepare_vectors(self):
        """Prepare TF-IDF vectors for all recipes"""
        recipe_texts = []
        for recipe in self.recipes:
            text_components = [
                ' '.join(recipe.get('ingredients', [])),
                recipe.get('cuisine', ''),
                recipe.get('difficulty', ''),
                ' '.join(recipe.get('dietary_info', []))
            ]
            recipe_texts.append(' '.join(text_components))
        
        if recipe_texts:
            self.recipe_vectors = self.vectorizer.fit_transform(recipe_texts)
    
    def get_ingredient_substitutions(self, ingredient):
        """Get substitution suggestions for an ingredient"""
        ingredient_lower = ingredient.lower()
        for key, substitutes in self.ingredient_substitutions.items():
            if key in ingredient_lower or ingredient_lower in key:
                return substitutes
        return []
    
    def filter_by_dietary_restrictions(self, recipes, restrictions):
        """Filter recipes based on dietary restrictions"""
        if not restrictions:
            return recipes
        
        filtered = []
        for recipe in recipes:
            dietary_info = recipe.get('dietary_info', [])
            
            # Check if recipe violates any restrictions
            violates_restriction = False
            for restriction in restrictions:
                if restriction == 'vegetarian':
                    meat_ingredients = ['chicken', 'beef', 'pork', 'lamb', 'fish', 'shrimp', 'bacon']
                    if any(meat in ' '.join(recipe.get('ingredients', [])).lower() for meat in meat_ingredients):
                        violates_restriction = True
                        break
                elif restriction == 'vegan':
                    if any(item in dietary_info for item in ['contains_dairy', 'contains_eggs']) or \
                       any(animal in ' '.join(recipe.get('ingredients', [])).lower() 
                           for animal in ['chicken', 'beef', 'pork', 'lamb', 'fish', 'shrimp', 'bacon', 'cheese', 'milk', 'butter', 'eggs']):
                        violates_restriction = True
                        break
                elif restriction == 'gluten_free' and 'contains_gluten' in dietary_info:
                    violates_restriction = True
                    break
                elif restriction == 'dairy_free' and 'contains_dairy' in dietary_info:
                    violates_restriction = True
                    break
            
            if not violates_restriction:
                filtered.append(recipe)
        
        return filtered
    
    def get_recommendations(self, ingredients, dietary_restrictions=None, max_cooking_time=None, 
                          difficulty=None, cuisine_preference=None, limit=10):
        """Get ML-powered recipe recommendations with advanced filtering"""
        
        if not self.recipes or not self.recipe_vectors:
            return []
        
        # Create enhanced query vector
        query_components = [' '.join(ingredients)]
        if cuisine_preference:
            query_components.append(cuisine_preference)
        if difficulty:
            query_components.append(difficulty)
        
        query_text = ' '.join(query_components)
        query_vector = self.vectorizer.transform([query_text])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_vector, self.recipe_vectors).flatten()
        
        # Start with all recipes
        candidates = list(self.recipes)
        
        # Apply dietary restrictions filter
        if dietary_restrictions:
            candidates = self.filter_by_dietary_restrictions(candidates, dietary_restrictions)
        
        # Calculate scores for remaining candidates
        recommendations = []
        for i, recipe in enumerate(candidates):
            # Find original index for similarity score
            original_index = next((idx for idx, r in enumerate(self.recipes) if r['id'] == recipe['id']), -1)
            if original_index == -1:
                continue
            
            # Apply additional filters
            if max_cooking_time and recipe.get('cooking_time', 0) > max_cooking_time:
                continue
            
            if difficulty and recipe.get('difficulty') != difficulty:
                continue
            
            if cuisine_preference and recipe.get('cuisine') != cuisine_preference:
                continue
            
            # Calculate ingredient match percentage
            recipe_ingredients = set(ing.lower() for ing in recipe.get('ingredients', []))
            query_ingredients = set(ing.lower() for ing in ingredients)
            
            # Direct ingredient matches
            direct_matches = len(recipe_ingredients.intersection(query_ingredients))
            ingredient_match_score = direct_matches / len(recipe_ingredients) if recipe_ingredients else 0
            
            # Coverage score (how many requested ingredients are covered)
            coverage_score = len(query_ingredients.intersection(recipe_ingredients)) / len(query_ingredients) if query_ingredients else 0
            
            # Combine ML similarity with ingredient matching
            ml_score = similarities[original_index]
            final_score = (ml_score * 0.4) + (ingredient_match_score * 0.4) + (coverage_score * 0.2)
            
            # Add recipe with enriched data
            recipe_copy = recipe.copy()
            recipe_copy['match_score'] = round(final_score * 100, 1)
            recipe_copy['ingredient_match_percentage'] = round(ingredient_match_score * 100, 1)
            recipe_copy['missing_ingredients'] = list(recipe_ingredients - query_ingredients)
            recipe_copy['substitution_suggestions'] = {}
            
            # Add substitution suggestions for missing ingredients
            for missing_ing in recipe_copy['missing_ingredients'][:3]:  # Limit to 3 suggestions
                substitutions = self.get_ingredient_substitutions(missing_ing)
                if substitutions:
                    recipe_copy['substitution_suggestions'][missing_ing] = substitutions[:2]
            
            recommendations.append(recipe_copy)
        
        # Sort by final score and return top results
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:limit]

class UserFeedbackSystem:
    """Handle user ratings and favorites"""
    
    def __init__(self):
        self.ratings_file = 'data/user_ratings.json'
        self.favorites_file = 'data/user_favorites.json'
        self._ensure_files()
    
    def _ensure_files(self):
        """Ensure feedback files exist"""
        for file_path in [self.ratings_file, self.favorites_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f)
    
    def add_rating(self, user_id, recipe_id, rating):
        """Add or update a recipe rating"""
        try:
            with open(self.ratings_file, 'r') as f:
                ratings = json.load(f)
            
            if user_id not in ratings:
                ratings[user_id] = {}
            
            ratings[user_id][str(recipe_id)] = {
                'rating': rating,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.ratings_file, 'w') as f:
                json.dump(ratings, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving rating: {e}")
            return False
    
    def toggle_favorite(self, user_id, recipe_id, is_favorite):
        """Toggle favorite status for a recipe"""
        try:
            with open(self.favorites_file, 'r') as f:
                favorites = json.load(f)
            
            if user_id not in favorites:
                favorites[user_id] = []
            
            if is_favorite and recipe_id not in favorites[user_id]:
                favorites[user_id].append(recipe_id)
            elif not is_favorite and recipe_id in favorites[user_id]:
                favorites[user_id].remove(recipe_id)
            
            with open(self.favorites_file, 'w') as f:
                json.dump(favorites, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error updating favorites: {e}")
            return False

# Initialize components
recipes = load_recipe_database()
ingredient_detector = IngredientDetector()
recommender = RecipeRecommendationEngine(recipes)
feedback_system = UserFeedbackSystem()

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Smart Recipe Generator is running',
        'features': {
            'ingredient_recognition': 'mock_implementation',
            'recipe_matching': 'ml_powered_tfidf_cosine_similarity',
            'substitution_suggestions': 'enabled',
            'dietary_restrictions': 'supported',
            'user_feedback': 'enabled'
        },
        'total_recipes': len(recipes),
        'ml_models_loaded': recommender.recipe_vectors is not None
    })

@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """Get list of available ingredients for autocomplete"""
    return jsonify({'ingredients': sorted(ingredient_detector.available_ingredients)})

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Ingredient detection from uploaded image"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Detect ingredients using mock implementation
        detection_result = ingredient_detector.detect_ingredients(filepath)
        
        return jsonify({
            'success': True,
            'ingredients': detection_result['ingredients'],
            'confidence_scores': detection_result['confidence_scores'],
            'total_detected': detection_result['total_detected'],
            'message': f'Detected {detection_result["total_detected"]} ingredients using computer vision',
            'mock_implementation': True
        })
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return jsonify({'error': 'Failed to process image'}), 500

@app.route('/api/recipes/suggest', methods=['POST'])
def suggest_recipes():
    """Get recipe suggestions based on ingredients using ML"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        ingredients = data.get('ingredients', [])
        dietary_restrictions = data.get('dietary_restrictions', [])
        max_cooking_time = data.get('max_cooking_time')
        difficulty = data.get('difficulty')
        cuisine_preference = data.get('cuisine_preference')
        
        if not ingredients:
            return jsonify({'error': 'No ingredients provided'}), 400
        
        # Get ML-powered recommendations
        recommendations = recommender.get_recommendations(
            ingredients=ingredients,
            dietary_restrictions=dietary_restrictions,
            max_cooking_time=max_cooking_time,
            difficulty=difficulty,
            cuisine_preference=cuisine_preference,
            limit=10
        )
        
        return jsonify({
            'success': True,
            'recipes': recommendations,
            'total_found': len(recommendations),
            'search_ingredients': ingredients,
            'ml_powered': True,
            'filters_applied': {
                'dietary_restrictions': dietary_restrictions,
                'max_cooking_time': max_cooking_time,
                'difficulty': difficulty,
                'cuisine_preference': cuisine_preference
            }
        })
        
    except Exception as e:
        logger.error(f"Error in suggest_recipes: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe_details(recipe_id):
    """Get detailed information about a specific recipe"""
    try:
        recipe = next((r for r in recipes if r['id'] == recipe_id), None)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        return jsonify({
            'success': True,
            'recipe': recipe
        })
        
    except Exception as e:
        logger.error(f"Error fetching recipe details: {str(e)}")
        return jsonify({'error': 'Failed to fetch recipe details'}), 500

@app.route('/api/recipes/<int:recipe_id>/rate', methods=['POST'])
def rate_recipe(recipe_id):
    """Rate a recipe (user feedback system)"""
    try:
        data = request.get_json()
        rating = data.get('rating')
        user_id = data.get('user_id', 'anonymous')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        success = feedback_system.add_rating(user_id, recipe_id, rating)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Recipe rated successfully',
                'rating': rating,
                'recipe_id': recipe_id
            })
        else:
            return jsonify({'error': 'Failed to save rating'}), 500
        
    except Exception as e:
        logger.error(f"Error in rate_recipe: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/recipes/<int:recipe_id>/favorite', methods=['POST'])
def toggle_favorite(recipe_id):
    """Toggle favorite status for a recipe"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')
        is_favorite = data.get('is_favorite', True)
        
        success = feedback_system.toggle_favorite(user_id, recipe_id, is_favorite)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Favorite status updated',
                'recipe_id': recipe_id,
                'is_favorite': is_favorite
            })
        else:
            return jsonify({'error': 'Failed to update favorite status'}), 500
        
    except Exception as e:
        logger.error(f"Error in toggle_favorite: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Smart Recipe Generator...")
    logger.info(f"Loaded {len(recipes)} recipes")
    logger.info("ML Models: TF-IDF + Cosine Similarity for recommendations")
    logger.info("Computer Vision: Mock detection for demo purposes")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
