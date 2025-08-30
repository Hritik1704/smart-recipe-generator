// Smart Recipe Generator - JavaScript Application

class SmartRecipeGenerator {
    constructor() {
        this.ingredients = [];
        this.availableIngredients = [];
        this.currentUser = 'user_' + Math.random().toString(36).substr(2, 9);
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadAvailableIngredients();
        this.checkSearchButton();
    }

    setupEventListeners() {
        // Image upload
        const uploadArea = document.getElementById('uploadArea');
        const imageInput = document.getElementById('imageInput');

        uploadArea.addEventListener('click', () => imageInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        imageInput.addEventListener('change', this.handleImageUpload.bind(this));

        // Manual ingredient input
        const ingredientInput = document.getElementById('ingredientInput');
        ingredientInput.addEventListener('input', this.handleIngredientInput.bind(this));
        ingredientInput.addEventListener('keydown', this.handleIngredientKeydown.bind(this));

        // Search button
        document.getElementById('searchBtn').addEventListener('click', this.searchRecipes.bind(this));

        // Modal
        document.getElementById('closeModal').addEventListener('click', this.closeModal.bind(this));
        document.getElementById('recipeModal').addEventListener('click', (e) => {
            if (e.target.id === 'recipeModal') this.closeModal();
        });

        // Close autocomplete when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.ingredient-input')) {
                this.hideAutocomplete();
            }
        });
    }

    async loadAvailableIngredients() {
        try {
            const response = await fetch('/api/ingredients');
            const data = await response.json();
            this.availableIngredients = data.ingredients;
        } catch (error) {
            console.error('Error loading ingredients:', error);
            this.showError('Failed to load ingredient suggestions');
        }
    }

    // Drag and drop handlers
    handleDragOver(e) {
        e.preventDefault();
        e.currentTarget.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.currentTarget.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processImageFile(files[0]);
        }
    }

    handleImageUpload(e) {
        const file = e.target.files[0];
        if (file) {
            this.processImageFile(file);
        }
    }

    async processImageFile(file) {
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('Please upload a valid image file (JPG, PNG, GIF, WebP, BMP)');
            return;
        }

        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            this.showError('File size must be less than 16MB');
            return;
        }

        const formData = new FormData();
        formData.append('image', file);

        try {
            this.showLoading('Analyzing image...');
            
            const response = await fetch('/api/upload-image', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            this.hideLoading();

            if (data.success) {
                this.displayDetectedIngredients(data.ingredients, data.confidence_scores);
                this.addIngredientsToSelection(data.ingredients);
                this.showSuccess(`Detected ${data.total_detected} ingredients from your image!`);
            } else {
                this.showError(data.error || 'Failed to process image');
            }
        } catch (error) {
            this.hideLoading();
            console.error('Error uploading image:', error);
            this.showError('Failed to process image. Please try again.');
        }
    }

    displayDetectedIngredients(ingredients, confidenceScores) {
        const uploadResult = document.getElementById('uploadResult');
        const detectedIngredients = document.getElementById('detectedIngredients');
        
        detectedIngredients.innerHTML = '';
        
        ingredients.forEach((ingredient, index) => {
            const confidence = confidenceScores[index];
            const tag = document.createElement('div');
            tag.className = 'ingredient-tag';
            tag.innerHTML = `
                ${ingredient}
                <span class="confidence">(${Math.round(confidence * 100)}%)</span>
            `;
            detectedIngredients.appendChild(tag);
        });
        
        uploadResult.style.display = 'block';
    }

    // Manual ingredient input handlers
    handleIngredientInput(e) {
        const query = e.target.value.toLowerCase().trim();
        
        if (query.length < 2) {
            this.hideAutocomplete();
            return;
        }

        const suggestions = this.availableIngredients
            .filter(ingredient => 
                ingredient.toLowerCase().includes(query) && 
                !this.ingredients.includes(ingredient)
            )
            .slice(0, 8);

        this.showAutocomplete(suggestions);
    }

    handleIngredientKeydown(e) {
        const suggestions = document.getElementById('autocompleteSuggestions');
        const highlighted = suggestions.querySelector('.highlighted');

        if (e.key === 'Enter') {
            e.preventDefault();
            if (highlighted) {
                this.addIngredient(highlighted.textContent);
            } else {
                const value = e.target.value.trim();
                if (value) {
                    this.addIngredient(value);
                }
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.highlightNext();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.highlightPrevious();
        } else if (e.key === 'Escape') {
            this.hideAutocomplete();
        }
    }

    showAutocomplete(suggestions) {
        const container = document.getElementById('autocompleteSuggestions');
        
        if (suggestions.length === 0) {
            this.hideAutocomplete();
            return;
        }

        container.innerHTML = '';
        suggestions.forEach(suggestion => {
            const div = document.createElement('div');
            div.className = 'autocomplete-suggestion';
            div.textContent = suggestion;
            div.addEventListener('click', () => this.addIngredient(suggestion));
            container.appendChild(div);
        });

        container.style.display = 'block';
    }

    hideAutocomplete() {
        document.getElementById('autocompleteSuggestions').style.display = 'none';
    }

    highlightNext() {
        const suggestions = document.querySelectorAll('.autocomplete-suggestion');
        const highlighted = document.querySelector('.autocomplete-suggestion.highlighted');
        
        if (!highlighted) {
            suggestions[0]?.classList.add('highlighted');
        } else {
            highlighted.classList.remove('highlighted');
            const next = highlighted.nextElementSibling || suggestions[0];
            next.classList.add('highlighted');
        }
    }

    highlightPrevious() {
        const suggestions = document.querySelectorAll('.autocomplete-suggestion');
        const highlighted = document.querySelector('.autocomplete-suggestion.highlighted');
        
        if (!highlighted) {
            suggestions[suggestions.length - 1]?.classList.add('highlighted');
        } else {
            highlighted.classList.remove('highlighted');
            const prev = highlighted.previousElementSibling || suggestions[suggestions.length - 1];
            prev.classList.add('highlighted');
        }
    }

    addIngredient(ingredient) {
        ingredient = ingredient.trim().toLowerCase();
        
        if (!ingredient || this.ingredients.includes(ingredient)) {
            document.getElementById('ingredientInput').value = '';
            this.hideAutocomplete();
            return;
        }

        this.ingredients.push(ingredient);
        this.updateSelectedIngredients();
        document.getElementById('ingredientInput').value = '';
        this.hideAutocomplete();
        this.checkSearchButton();
    }

    addIngredientsToSelection(newIngredients) {
        newIngredients.forEach(ingredient => {
            const lowerIngredient = ingredient.toLowerCase();
            if (!this.ingredients.includes(lowerIngredient)) {
                this.ingredients.push(lowerIngredient);
            }
        });
        this.updateSelectedIngredients();
        this.checkSearchButton();
    }

    removeIngredient(ingredient) {
        this.ingredients = this.ingredients.filter(i => i !== ingredient);
        this.updateSelectedIngredients();
        this.checkSearchButton();
    }

    updateSelectedIngredients() {
        const container = document.getElementById('selectedIngredients');
        container.innerHTML = '';

        this.ingredients.forEach(ingredient => {
            const tag = document.createElement('div');
            tag.className = 'ingredient-tag';
            tag.innerHTML = `
                ${ingredient}
                <span class="remove" onclick="app.removeIngredient('${ingredient}')">&times;</span>
            `;
            container.appendChild(tag);
        });
    }

    checkSearchButton() {
        const searchBtn = document.getElementById('searchBtn');
        searchBtn.disabled = this.ingredients.length === 0;
    }

    async searchRecipes() {
        if (this.ingredients.length === 0) {
            this.showError('Please add at least one ingredient');
            return;
        }

        const filters = this.getFilters();
        const requestData = {
            ingredients: this.ingredients,
            ...filters
        };

        try {
            this.showLoading('Finding perfect recipes for you...');
            
            const response = await fetch('/api/recipes/suggest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();
            this.hideLoading();

            if (data.success) {
                this.displayResults(data);
                if (data.recipes.length === 0) {
                    this.showError('No recipes found matching your criteria. Try removing some filters or adding different ingredients.');
                }
            } else {
                this.showError(data.error || 'Failed to search recipes');
            }
        } catch (error) {
            this.hideLoading();
            console.error('Error searching recipes:', error);
            this.showError('Failed to search recipes. Please try again.');
        }
    }

    getFilters() {
        const dietaryRestrictions = Array.from(document.getElementById('dietaryRestrictions').selectedOptions)
            .map(option => option.value);
        
        const maxCookingTime = document.getElementById('maxCookingTime').value;
        const difficulty = document.getElementById('difficulty').value;
        const cuisine = document.getElementById('cuisine').value;

        return {
            dietary_restrictions: dietaryRestrictions,
            max_cooking_time: maxCookingTime ? parseInt(maxCookingTime) : null,
            difficulty: difficulty || null,
            cuisine_preference: cuisine || null
        };
    }

    displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsInfo = document.getElementById('resultsInfo');
        const recipesGrid = document.getElementById('recipesGrid');

        resultsInfo.textContent = `Found ${data.total_found} recipes matching your ingredients: ${data.search_ingredients.join(', ')}`;
        
        recipesGrid.innerHTML = '';
        
        data.recipes.forEach(recipe => {
            const recipeCard = this.createRecipeCard(recipe);
            recipesGrid.appendChild(recipeCard);
        });

        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    createRecipeCard(recipe) {
        const card = document.createElement('div');
        card.className = 'recipe-card';
        card.addEventListener('click', () => this.showRecipeDetails(recipe.id));

        const matchedIngredients = recipe.ingredients.filter(ing => 
            this.ingredients.some(userIng => ing.toLowerCase().includes(userIng))
        );

        const substitutionsHtml = Object.keys(recipe.substitution_suggestions || {}).length > 0 
            ? `<div class="substitutions">
                <h4><i class="fas fa-exchange-alt"></i> Suggested Substitutions:</h4>
                ${Object.entries(recipe.substitution_suggestions).map(([ingredient, subs]) => 
                    `<div class="substitution-item">
                        <strong>${ingredient}:</strong> ${subs.join(', ')}
                    </div>`
                ).join('')}
            </div>` 
            : '';

        card.innerHTML = `
            <div class="recipe-header">
                <h3 class="recipe-title">${recipe.name}</h3>
                <div class="recipe-meta">
                    <span><i class="fas fa-globe"></i> ${recipe.cuisine}</span>
                    <span><i class="fas fa-clock"></i> ${recipe.cooking_time} min</span>
                    <span><i class="fas fa-signal"></i> ${recipe.difficulty}</span>
                    <span><i class="fas fa-users"></i> ${recipe.servings} servings</span>
                </div>
                <div class="match-score">
                    <i class="fas fa-percentage"></i>
                    ${recipe.match_score}% Match
                </div>
            </div>
            <div class="recipe-body">
                <div class="recipe-ingredients">
                    <h4>Ingredients:</h4>
                    <div class="ingredients-list">
                        ${recipe.ingredients.map(ingredient => {
                            const isMatched = matchedIngredients.includes(ingredient);
                            return `<span class="ingredient-item ${isMatched ? 'matched' : ''}">${ingredient}</span>`;
                        }).join('')}
                    </div>
                </div>
                ${substitutionsHtml}
            </div>
        `;

        return card;
    }

    async showRecipeDetails(recipeId) {
        try {
            const response = await fetch(`/api/recipes/${recipeId}`);
            const data = await response.json();

            if (data.success) {
                this.displayRecipeModal(data.recipe);
            } else {
                this.showError('Failed to load recipe details');
            }
        } catch (error) {
            console.error('Error loading recipe details:', error);
            this.showError('Failed to load recipe details');
        }
    }

    displayRecipeModal(recipe) {
        const modalBody = document.getElementById('modalBody');
        
        modalBody.innerHTML = `
            <div class="recipe-detail">
                <h2>${recipe.name}</h2>
                <div class="recipe-meta-detailed">
                    <div class="meta-item">
                        <i class="fas fa-globe"></i>
                        <span><strong>Cuisine:</strong> ${recipe.cuisine}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-clock"></i>
                        <span><strong>Total Time:</strong> ${recipe.total_time || recipe.cooking_time} minutes</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-signal"></i>
                        <span><strong>Difficulty:</strong> ${recipe.difficulty}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-users"></i>
                        <span><strong>Servings:</strong> ${recipe.servings}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-star"></i>
                        <span><strong>Rating:</strong> ${recipe.rating}/5 (${recipe.ratings_count} reviews)</span>
                    </div>
                </div>

                <div class="recipe-section">
                    <h3><i class="fas fa-list"></i> Ingredients</h3>
                    <ul class="ingredients-detailed">
                        ${recipe.ingredients.map(ingredient => `<li>${ingredient}</li>`).join('')}
                    </ul>
                </div>

                <div class="recipe-section">
                    <h3><i class="fas fa-clipboard-list"></i> Instructions</h3>
                    <ol class="instructions-list">
                        ${recipe.instructions.map(instruction => `<li>${instruction}</li>`).join('')}
                    </ol>
                </div>

                <div class="recipe-section">
                    <h3><i class="fas fa-chart-pie"></i> Nutrition Information</h3>
                    <div class="nutrition-grid">
                        <div class="nutrition-item">
                            <span class="nutrition-label">Calories:</span>
                            <span class="nutrition-value">${recipe.nutrition.calories}</span>
                        </div>
                        <div class="nutrition-item">
                            <span class="nutrition-label">Protein:</span>
                            <span class="nutrition-value">${recipe.nutrition.protein}g</span>
                        </div>
                        <div class="nutrition-item">
                            <span class="nutrition-label">Carbs:</span>
                            <span class="nutrition-value">${recipe.nutrition.carbs}g</span>
                        </div>
                        <div class="nutrition-item">
                            <span class="nutrition-label">Fat:</span>
                            <span class="nutrition-value">${recipe.nutrition.fat}g</span>
                        </div>
                    </div>
                </div>

                <div class="recipe-actions">
                    <div class="rating-section">
                        <h4>Rate this recipe:</h4>
                        <div class="star-rating" data-recipe-id="${recipe.id}">
                            ${[1,2,3,4,5].map(star => 
                                `<i class="fas fa-star star" data-rating="${star}"></i>`
                            ).join('')}
                        </div>
                    </div>
                    <button class="favorite-btn" data-recipe-id="${recipe.id}">
                        <i class="fas fa-heart"></i>
                        Add to Favorites
                    </button>
                </div>
            </div>
        `;

        // Add event listeners for rating and favorites
        this.setupModalEventListeners(recipe.id);
        
        document.getElementById('recipeModal').style.display = 'flex';
    }

    setupModalEventListeners(recipeId) {
        // Star rating
        const stars = document.querySelectorAll('.star-rating .star');
        stars.forEach(star => {
            star.addEventListener('click', (e) => {
                const rating = parseInt(e.target.dataset.rating);
                this.rateRecipe(recipeId, rating);
                this.updateStarDisplay(rating);
            });
            
            star.addEventListener('mouseenter', (e) => {
                const rating = parseInt(e.target.dataset.rating);
                this.highlightStars(rating);
            });
        });

        document.querySelector('.star-rating').addEventListener('mouseleave', () => {
            this.resetStars();
        });

        // Favorite button
        const favoriteBtn = document.querySelector('.favorite-btn');
        favoriteBtn.addEventListener('click', () => {
            this.toggleFavorite(recipeId);
        });
    }

    async rateRecipe(recipeId, rating) {
        try {
            const response = await fetch(`/api/recipes/${recipeId}/rate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    rating: rating,
                    user_id: this.currentUser
                })
            });

            const data = await response.json();
            if (data.success) {
                this.showSuccess(`Rated recipe ${rating} stars!`);
            } else {
                this.showError('Failed to rate recipe');
            }
        } catch (error) {
            console.error('Error rating recipe:', error);
            this.showError('Failed to rate recipe');
        }
    }

    async toggleFavorite(recipeId) {
        try {
            const response = await fetch(`/api/recipes/${recipeId}/favorite`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    is_favorite: true,
                    user_id: this.currentUser
                })
            });

            const data = await response.json();
            if (data.success) {
                this.showSuccess('Added to favorites!');
                const btn = document.querySelector('.favorite-btn');
                btn.innerHTML = '<i class="fas fa-heart" style="color: red;"></i> Favorited';
                btn.disabled = true;
            } else {
                this.showError('Failed to add to favorites');
            }
        } catch (error) {
            console.error('Error adding to favorites:', error);
            this.showError('Failed to add to favorites');
        }
    }

    highlightStars(rating) {
        const stars = document.querySelectorAll('.star-rating .star');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.style.color = '#fbbf24';
            } else {
                star.style.color = '#d1d5db';
            }
        });
    }

    updateStarDisplay(rating) {
        this.highlightStars(rating);
    }

    resetStars() {
        const stars = document.querySelectorAll('.star-rating .star');
        stars.forEach(star => {
            star.style.color = '#d1d5db';
        });
    }

    closeModal() {
        document.getElementById('recipeModal').style.display = 'none';
    }

    showLoading(message = 'Loading...') {
        const loading = document.getElementById('loading');
        loading.querySelector('p').textContent = message;
        loading.style.display = 'block';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    showError(message) {
        const toast = document.getElementById('errorToast');
        document.getElementById('errorMessage').textContent = message;
        toast.style.display = 'block';
        
        setTimeout(() => {
            toast.style.display = 'none';
        }, 5000);
    }

    showSuccess(message) {
        const toast = document.getElementById('successToast');
        document.getElementById('successMessage').textContent = message;
        toast.style.display = 'block';
        
        setTimeout(() => {
            toast.style.display = 'none';
        }, 3000);
    }
}

// Initialize the application
const app = new SmartRecipeGenerator();
