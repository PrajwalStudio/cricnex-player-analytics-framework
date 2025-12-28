# CricNex Frontend

Professional React-based frontend for the CricNex Cricket Player Performance Prediction System.

## Features

- **Dashboard**: Overview of system statistics and model performance
- **Prediction**: Real-time player performance prediction with **ML model selection** (XGBoost, Random Forest, LSTM, ARIMA)
- **Players**: Browse and search player profiles with detailed statistics
- **Leaderboard**: Top performers across multiple metrics
- **Teams**: IPL team rosters and player listings (2023-2025 teams)
- **Analytics**: Advanced performance analytics and matchup analysis

## Key Highlights

✅ **Multi-Model Support**: Choose from 4 ML models in the prediction interface  
✅ **Model Metrics**: View RMSE scores for each model before selection  
✅ **Smart Filtering**: Recent IPL teams only, opponent auto-filtering  
✅ **Professional UI**: Gradient purple theme with dark sidebar navigation  
✅ **Responsive Design**: Works on desktop, tablet, and mobile  
✅ **Real-time API**: 18 REST endpoints with full CORS support

## Tech Stack

- React 18
- React Router v6
- Axios for API calls
- Recharts for data visualization
- Lucide React for icons
- CSS3 with responsive design

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

## Configuration

The API base URL is configured in `src/services/api.js`:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

Make sure the backend server is running before starting the frontend.

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Layout.js       # Main layout with sidebar
│   │   ├── Layout.css
│   │   ├── StatCard.js     # Reusable stat card component
│   │   └── StatCard.css
│   ├── pages/
│   │   ├── Dashboard.js    # Dashboard page
│   │   ├── Prediction.js   # Prediction page
│   │   ├── Players.js      # Players listing
│   │   ├── Leaderboard.js  # Leaderboard page
│   │   ├── Teams.js        # Teams page
│   │   └── Analytics.js    # Analytics page
│   ├── services/
│   │   └── api.js         # API service layer
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
└── package.json
```

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm eject` - Ejects from Create React App (one-way operation)

## Features by Page

### Dashboard
- System overview with key metrics
- Model information and performance
- Top run scorers visualization
- System status indicators

### Prediction
- Player search with autocomplete
- Team and venue selection (recent IPL teams 2023-2025)
- **ML Model selector** with 4 options (XGBoost, Random Forest, LSTM, ARIMA)
- Model performance metrics displayed (RMSE scores)
- Smart opponent filtering (excludes selected team)
- Real-time prediction results
- Confidence metrics and key factors

### Players
- Searchable player list
- Sortable by multiple metrics
- Detailed player profiles
- Recent form and performance history

### Leaderboard
- Multiple leaderboard views (Runs, Strike Rate, Average)
- Tabbed interface
- Medal system for top 3 players
- Responsive table design

### Teams
- All IPL teams grid
- Team selection
- Squad listings with player stats
- Interactive team cards

### Analytics
- Recent form trends visualization
- Player vs team matchup analysis
- Performance history
- Interactive charts

## Responsive Design

The application is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development

To add a new page:

1. Create page component in `src/pages/`
2. Create corresponding CSS file
3. Add route in `src/App.js`
4. Add navigation item in `src/components/Layout.js`

## Production Build

To create a production build:

```bash
npm run build
```

The build folder will contain optimized production files ready for deployment.

## API Integration

All API calls are centralized in `src/services/api.js`. The service provides functions for:
- Health checks
- Player data
- Predictions
- Teams and venues
- Leaderboards
- Analytics

## Styling

- Professional gradient design
- Consistent color scheme
- Smooth animations and transitions
- Card-based layout
- Modern UI patterns

## License

Part of the CricNex project.
