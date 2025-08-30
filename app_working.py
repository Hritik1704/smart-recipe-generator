from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
import random
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class SimpleRecipeRecommender:
    def __init__(self):
        self.recipes = []
        self.all_ingredients = set()
        self.load_recipes()
        
    def load_recipes(self):
        """Load recipes from JSON file"""
        try:
            with open('data/recipes.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.recipes = data.get('recipes', [])
                
            # Extract all unique ingredients for autocomplete
            for recipe in self.recipes:
                for ingredient in recipe.get('ingredients', []):
                    self.all_ingredients.add(ingredient.lower().strip())
                    
            logger.info(f"Loaded {len(self.recipes)} recipes")
            
        except Exception as e:
            logger.error(f"Error loading recipes: {e}")
            self.recipes = []
    
    def get_recommendations(self, ingredients, dietary_restrictions=None, max_cooking_time=None, 
                          difficulty=None, cuisine_preference=None, limit=10):
        """Get recipe recommendations based on ingredients and filters"""
        try:
            if not ingredients:
                return []
            
            # Normalize input ingredients
            query_ingredients = set(ing.lower().strip() for ing in ingredients)
            recommendations = []
            
            for recipe in self.recipes:
                try:
                    # Apply dietary restrictions filter
                    if dietary_restrictions:
                        recipe_dietary = recipe.get('dietary_info', {})
                        if not self._matches_dietary_restrictions(recipe_dietary, dietary_restrictions):
                            continue
                    
                    # Apply other filters
                    if max_cooking_time and recipe.get('cooking_time', 0) > max_cooking_time:
                        continue
                    
                    if difficulty and recipe.get('difficulty', '').lower() != difficulty.lower():
                        continue
                    
                    if cuisine_preference and recipe.get('cuisine', '').lower() != cuisine_preference.lower():
                        continue
                    
                    # Calculate ingredient matching score
                    recipe_ingredients = set(ing.lower().strip() for ing in recipe.get('ingredients', []))
                    
                    # Direct matches
                    direct_matches = len(recipe_ingredients.intersection(query_ingredients))
                    total_recipe_ingredients = len(recipe_ingredients)
                    
                    if total_recipe_ingredients == 0:
                        continue
                    
                    # Calculate scores
                    ingredient_match_score = direct_matches / total_recipe_ingredients
                    coverage_score = len(query_ingredients.intersection(recipe_ingredients)) / len(query_ingredients)
                    
                    # Simple scoring algorithm
                    final_score = (ingredient_match_score * 0.6) + (coverage_score * 0.4)
                    
                    # Only include recipes with some ingredient match
                    if direct_matches > 0:
                        recipe_copy = recipe.copy()
                        recipe_copy['match_score'] = round(final_score * 100, 1)
                        recipe_copy['ingredient_match_percentage'] = round(ingredient_match_score * 100, 1)
                        recipe_copy['missing_ingredients'] = list(recipe_ingredients - query_ingredients)
                        
                        # Add substitution suggestions for top missing ingredients
                        missing_ingredients = list(recipe_ingredients - query_ingredients)
                        recipe_copy['substitution_suggestions'] = self._get_substitutions(missing_ingredients[:3])
                        
                        recommendations.append(recipe_copy)
                        
                except Exception as e:
                    logger.error(f"Error processing recipe {recipe.get('name', 'Unknown')}: {e}")
                    continue
            
            # Sort by match score and return top results
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error in get_recommendations: {e}")
            return []
    
    def _matches_dietary_restrictions(self, recipe_dietary, restrictions):
        """Check if recipe matches dietary restrictions"""
        for restriction in restrictions:
            restriction = restriction.lower()
            if restriction == 'vegetarian' and not recipe_dietary.get('vegetarian', False):
                return False
            elif restriction == 'vegan' and not recipe_dietary.get('vegan', False):
                return False
            elif restriction == 'gluten-free' and not recipe_dietary.get('gluten_free', False):
                return False
            elif restriction == 'dairy-free' and not recipe_dietary.get('dairy_free', False):
                return False
        return True
    
    def _get_substitutions(self, missing_ingredients):
        """Get substitution suggestions for missing ingredients"""
        substitutions = {
            'butter': ['olive oil', 'coconut oil'],
            'milk': ['almond milk', 'soy milk'],
            'eggs': ['flax eggs', 'applesauce'],
            'flour': ['almond flour', 'coconut flour'],
            'sugar': ['honey', 'maple syrup'],
            'cream': ['coconut cream', 'cashew cream'],
            'cheese': ['nutritional yeast', 'cashew cheese'],
            'chicken': ['tofu', 'tempeh'],
            'beef': ['mushrooms', 'lentils'],
            'oil': ['butter', 'ghee'],
            'onion': ['shallots', 'garlic'],
            'garlic': ['garlic powder', 'onion powder']
        }
        
        suggestions = {}
        for ingredient in missing_ingredients[:3]:  # Limit to top 3
            ingredient_lower = ingredient.lower()
            for key, subs in substitutions.items():
                if key in ingredient_lower:
                    suggestions[ingredient] = subs[:2]  # Max 2 substitutes
                    break
        
        return suggestions

class MockIngredientDetector:
    """Mock computer vision for ingredient detection"""
    
    def __init__(self):
        # Common ingredients for mock detection
        self.mock_ingredients = [
            'tomatoes', 'onions', 'garlic', 'carrots', 'potatoes', 'bell peppers',
            'mushrooms', 'spinach', 'broccoli', 'chicken', 'beef', 'eggs',
            'cheese', 'milk', 'butter', 'olive oil', 'salt', 'pepper',
            'basil', 'oregano', 'thyme', 'parsley', 'lemon', 'ginger'
        ]
    
    def detect_ingredients(self, image_path):
        """Mock ingredient detection - returns random ingredients"""
        try:
            # Simulate processing time and return random ingredients
            num_ingredients = random.randint(3, 8)
            detected = random.sample(self.mock_ingredients, num_ingredients)
            
            results = []
            for ingredient in detected:
                results.append({
                    'name': ingredient,
                    'confidence': round(random.uniform(0.7, 0.95), 2)
                })
            
            return sorted(results, key=lambda x: x['confidence'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error in mock ingredient detection: {e}")
            return []

# Initialize components
recommender = SimpleRecipeRecommender()
ingredient_detector = MockIngredientDetector()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_user_data(filename):
    """Load user data from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
    return {}

def save_user_data(filename, data):
    """Save user data to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving {filename}: {e}")
        return False

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """Get all available ingredients for autocomplete"""
    try:
        return jsonify({
            'success': True,
            'ingredients': sorted(list(recommender.all_ingredients))
        })
    except Exception as e:
        logger.error(f"Error in get_ingredients: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Handle image upload and ingredient detection"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Mock ingredient detection
            detected_ingredients = ingredient_detector.detect_ingredients(filepath)
            
            return jsonify({
                'success': True,
                'detected_ingredients': detected_ingredients,
                'message': f'Detected {len(detected_ingredients)} ingredients'
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
            
    except Exception as e:
        logger.error(f"Error in upload_image: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recipes/suggest', methods=['POST'])
def suggest_recipes():
    """Get recipe suggestions based on ingredients and preferences"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        ingredients = data.get('ingredients', [])
        if not ingredients:
            return jsonify({'success': False, 'error': 'No ingredients provided'}), 400
        
        # Get filters
        dietary_restrictions = data.get('dietary_restrictions', [])
        max_cooking_time = data.get('max_cooking_time')
        difficulty = data.get('difficulty')
        cuisine_preference = data.get('cuisine_preference')
        limit = data.get('limit', 10)
        
        # Convert cooking time to integer if provided
        if max_cooking_time:
            try:
                max_cooking_time = int(max_cooking_time)
            except (ValueError, TypeError):
                max_cooking_time = None
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            ingredients=ingredients,
            dietary_restrictions=dietary_restrictions,
            max_cooking_time=max_cooking_time,
            difficulty=difficulty,
            cuisine_preference=cuisine_preference,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'recipes': recommendations,
            'count': len(recommendations),
            'message': f'Found {len(recommendations)} matching recipes'
        })
        
    except Exception as e:
        logger.error(f"Error in suggest_recipes: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recipes/<int:recipe_id>/rate', methods=['POST'])
def rate_recipe(recipe_id):
    """Rate a recipe"""
    try:
        data = request.get_json()
        rating = data.get('rating')
        
        if not rating or not (1 <= rating <= 5):
            return jsonify({'success': False, 'error': 'Invalid rating'}), 400
        
        # Load existing ratings
        ratings = load_user_data('data/user_ratings.json')
        ratings[str(recipe_id)] = rating
        
        # Save ratings
        if save_user_data('data/user_ratings.json', ratings):
            return jsonify({'success': True, 'message': 'Rating saved successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save rating'}), 500
            
    except Exception as e:
        logger.error(f"Error in rate_recipe: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recipes/<int:recipe_id>/favorite', methods=['POST'])
def toggle_favorite(recipe_id):
    """Toggle recipe favorite status"""
    try:
        # Load existing favorites
        favorites = load_user_data('data/user_favorites.json')
        
        # Toggle favorite status
        recipe_id_str = str(recipe_id)
        if recipe_id_str in favorites:
            del favorites[recipe_id_str]
            is_favorite = False
            message = 'Removed from favorites'
        else:
            favorites[recipe_id_str] = True
            is_favorite = True
            message = 'Added to favorites'
        
        # Save favorites
        if save_user_data('data/user_favorites.json', favorites):
            return jsonify({
                'success': True,
                'is_favorite': is_favorite,
                'message': message
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to save favorite'}), 500
            
    except Exception as e:
        logger.error(f"Error in toggle_favorite: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user/data', methods=['GET'])
def get_user_data():
    """Get user ratings and favorites"""
    try:
        ratings = load_user_data('data/user_ratings.json')
        favorites = load_user_data('data/user_favorites.json')
        
        return jsonify({
            'success': True,
            'ratings': ratings,
            'favorites': favorites
        })
        
    except Exception as e:
        logger.error(f"Error in get_user_data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Smart Recipe Generator...")
    logger.info(f"Loaded {len(recommender.recipes)} recipes")
    logger.info("Simple scoring algorithm for recommendations")
    logger.info("Computer Vision: Mock detection for demo purposes")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
