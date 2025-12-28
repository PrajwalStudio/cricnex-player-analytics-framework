import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// System APIs
export const getHealth = () => api.get('/health');
export const getModelInfo = () => api.get('/model/info');
export const getStatsSummary = () => api.get('/stats/summary');
export const getModels = () => api.get('/models');

// Prediction APIs
export const predictPerformance = (data) => api.post('/predict', data);
export const predictBatch = (data) => api.post('/predict/batch', data);

// Player APIs
export const getPlayers = (params) => api.get('/players', { params });
export const searchPlayers = (query) => api.get('/players/search', { params: { q: query } });
export const getPlayerDetails = (playerName) => api.get(`/players/${playerName}`);

// Team APIs
export const getTeams = () => api.get('/teams');
export const getTeamPlayers = (teamName) => api.get(`/teams/${teamName}/players`);

// Venue APIs
export const getVenues = (params) => api.get('/venues', { params });
export const getVenueStats = (venueName) => api.get(`/venues/${venueName}/stats`);

// Leaderboard APIs
export const getTopRunScorers = (params) => api.get('/leaderboard/runs', { params });
export const getTopStrikeRates = (params) => api.get('/leaderboard/strike-rate', { params });
export const getTopAverages = (params) => api.get('/leaderboard/average', { params });

// Comparison APIs
export const comparePlayers = (players) => api.post('/compare/players', { players });

// Analytics APIs
export const getRecentForm = (params) => api.get('/analytics/form', { params });
export const getPlayerMatchups = (params) => api.get('/analytics/matchups', { params });

export default api;
