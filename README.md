# Smart Recipe Generator - React App

A modern React application that uses Google Gemini AI to generate personalized recipes based on available ingredients and dietary preferences.

## Features

- **AI-Powered Recipe Generation**: Uses Google Gemini 2.0 Flash model for intelligent recipe creation
- **Ingredient-Based Suggestions**: Input available ingredients and get customized recipes
- **Dietary Preferences**: Specify cuisine types, dietary restrictions, or cooking preferences
- **Beautiful UI**: Modern, responsive design with smooth animations
- **Real-time Generation**: Fast recipe generation with loading states
- **Mobile Friendly**: Fully responsive design for all devices

## Technologies Used

- **React 18** - Modern React with hooks
- **Google Gemini API** - AI-powered recipe generation
- **Lucide React** - Beautiful icons
- **CSS3** - Modern styling with gradients and animations
- **Axios** - HTTP client for API requests

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn package manager
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Hritik1704/smart-recipe-generator.git
cd smart-recipe-generator-react
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Building for Production

```bash
npm run build
```

This builds the app for production to the `build` folder.

## How to Use

1. **Enter Ingredients**: Type in the ingredients you have available (comma-separated)
2. **Add Preferences** (Optional): Specify dietary restrictions, cuisine type, or cooking style
3. **Generate Recipe**: Click the "Generate Recipe" button
4. **View Results**: Get a detailed recipe with ingredients, instructions, cooking time, and tips
5. **Generate New**: Click "New Recipe" to start over with different ingredients

## API Integration

This app uses the Google Gemini 2.0 Flash model via the Generative Language API:

- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
- **Authentication**: API key-based authentication
- **Response Format**: Structured JSON with recipe details

## Project Structure

```
src/
├── App.js          # Main application component
├── App.css         # Application-specific styles
├── index.js        # React DOM entry point
├── index.css       # Global styles
public/
├── index.html      # HTML template
package.json        # Project dependencies and scripts
```

## Features in Detail

### Recipe Generation
- Intelligent parsing of ingredients
- Context-aware recipe suggestions
- Structured output with cooking details

### User Interface
- Clean, modern design
- Intuitive ingredient input
- Real-time loading states
- Error handling and user feedback

### Responsive Design
- Mobile-first approach
- Flexible layouts
- Touch-friendly interactions

## Deployment

This app can be deployed to various platforms:

- **Netlify**: Connect your GitHub repository for automatic deployments
- **Vercel**: Deploy with zero configuration
- **GitHub Pages**: Use `npm run build` and deploy the build folder

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Google Gemini AI for powerful recipe generation
- React team for the excellent framework
- Lucide for beautiful icons
