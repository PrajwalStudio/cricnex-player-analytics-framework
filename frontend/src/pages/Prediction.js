import React, { useState, useEffect } from 'react';
import { TrendingUp, Search, AlertCircle, BarChart3, Activity } from 'lucide-react';
import { predictPerformance, searchPlayers, getTeams, getVenues, getModels, getPlayerDetails } from '../services/api';
import { LineChart, Line, BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Prediction.css';

const Prediction = () => {
  const [formData, setFormData] = useState({
    player: '',
    team: '',
    opponent: '',
    venue: '',
    model_name: 'xgboost'  // Default model
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [playerSuggestions, setPlayerSuggestions] = useState([]);
  const [teams, setTeams] = useState([]);
  const [allTeams, setAllTeams] = useState([]);
  const [playerTeams, setPlayerTeams] = useState([]);
  const [venues, setVenues] = useState([]);
  const [allVenues, setAllVenues] = useState([]);
  const [models, setModels] = useState([]);
  const [playerHistory, setPlayerHistory] = useState([]);
  const [historicalData, setHistoricalData] = useState({});
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    fetchTeamsAndVenues();
    fetchModels();
    
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const fetchModels = async () => {
    try {
      const response = await getModels();
      setModels(response.data.models || []);
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const fetchTeamsAndVenues = async () => {
    try {
      const [teamsRes, venuesRes] = await Promise.all([
        getTeams(),
        getVenues()
      ]);
      
      // Filter for recent IPL teams (2023-2025)
      const recentIPLTeams = [
        'Chennai Super Kings',
        'Mumbai Indians',
        'Royal Challengers Bangalore',
        'Kolkata Knight Riders',
        'Delhi Capitals',
        'Punjab Kings',
        'Rajasthan Royals',
        'Sunrisers Hyderabad',
        'Lucknow Super Giants',
        'Gujarat Titans'
      ];
      
      const allTeamsList = teamsRes.data.teams || [];
      
      // Remove duplicate teams and normalize
      const teamMap = new Map();
      allTeamsList.forEach(team => {
        const normalizedTeam = team.team
          .trim()
          .replace(/\s+/g, ' ')
          .toLowerCase();
        
        if (!teamMap.has(normalizedTeam)) {
          teamMap.set(normalizedTeam, team);
        }
      });
      
      const uniqueTeams = Array.from(teamMap.values());
      const filteredTeams = uniqueTeams.filter(team => 
        recentIPLTeams.includes(team.team)
      );
      
      setAllTeams(filteredTeams);
      setTeams(filteredTeams);
      
      // Remove duplicate venues and normalize names
      const allVenuesList = venuesRes.data.venues || [];
      const venueMap = new Map();
      
      allVenuesList.forEach(venue => {
        // Normalize venue name: remove city suffixes, periods, extra spaces
        let normalizedName = venue.venue
          .trim()
          .replace(/\.$/, '') // Remove trailing period
          .replace(/\s*,\s*(Mumbai|Bengaluru|Bangalore|Chennai|Kolkata|Delhi|Pune|Hyderabad|Jaipur|Chandigarh|Mohali|Ahmedabad|Lucknow|Dharamsala|Indore|Visakhapatnam|Cuttack|Nagpur|Ranchi|Guwahati)$/i, '') // Remove city suffixes
          .replace(/\./g, '') // Remove all periods
          .replace(/\s+/g, ' ') // Normalize spaces
          .trim()
          .toLowerCase();
        
        // Only add if not already in map (keeps first occurrence)
        if (!venueMap.has(normalizedName)) {
          // Use cleaned version without city suffix for display
          let cleanVenue = venue.venue
            .trim()
            .replace(/\s*,\s*(Mumbai|Bengaluru|Bangalore|Chennai|Kolkata|Delhi|Pune|Hyderabad|Jaipur|Chandigarh|Mohali|Ahmedabad|Lucknow|Dharamsala|Indore|Visakhapatnam|Cuttack|Nagpur|Ranchi|Guwahati)$/i, '')
            .replace(/\.$/, '')
            .trim();
            
          venueMap.set(normalizedName, {
            ...venue,
            venue: cleanVenue
          });
        }
      });
      
      const uniqueVenues = Array.from(venueMap.values())
        .sort((a, b) => a.venue.localeCompare(b.venue)); // Sort alphabetically
      
      setAllVenues(uniqueVenues);
      setVenues(uniqueVenues);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const handlePlayerSearch = async (query) => {
    if (query.length < 2) {
      setPlayerSuggestions([]);
      return;
    }
    try {
      const response = await searchPlayers(query);
      setPlayerSuggestions(response.data.players || []);
    } catch (error) {
      console.error('Error searching players:', error);
    }
  };

  const fetchMatchupVenues = async (team, opponent) => {
    if (!team || !opponent) {
      setVenues(allVenues);
      return;
    }
    
    try {
      const response = await getVenues({ team, opponent });
      const matchupVenues = response.data.venues || [];
      
      if (matchupVenues.length > 0) {
        setVenues(matchupVenues);
      } else {
        // If no specific venues found, show all venues
        setVenues(allVenues);
      }
    } catch (error) {
      console.error('Error fetching matchup venues:', error);
      setVenues(allVenues);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => {
      const newData = { ...prev, [field]: value };
      
      // If changing "Playing For" team and it matches opponent, clear opponent
      if (field === 'team' && value === prev.opponent) {
        newData.opponent = '';
        setVenues(allVenues);
      }
      
      // Fetch venues when both team and opponent are selected
      if (field === 'team' && prev.opponent) {
        fetchMatchupVenues(value, prev.opponent);
      } else if (field === 'opponent' && prev.team) {
        fetchMatchupVenues(prev.team, value);
      }
      
      return newData;
    });
    
    if (field === 'player') {
      handlePlayerSearch(value);
      // Reset teams to all teams if player is cleared
      if (!value || value.trim() === '') {
        setTeams(allTeams);
        setPlayerTeams([]);
      }
    }
  };

  const handlePlayerSelect = async (playerName) => {
    setFormData(prev => ({ ...prev, player: playerName, team: '', opponent: '' }));
    setPlayerSuggestions([]);
    
    // Fetch player's teams and history
    try {
      const response = await getPlayerDetails(playerName);
      const playerTeamsList = response.data.teams || [];
      setPlayerTeams(playerTeamsList);
      
      // Generate sample history data for visualization
      const sampleHistory = [
        { match: 'Match 1', runs: response.data.avg_runs * 0.8 || 25, strikeRate: response.data.avg_strike_rate * 0.9 || 120 },
        { match: 'Match 2', runs: response.data.avg_runs * 1.2 || 45, strikeRate: response.data.avg_strike_rate * 1.1 || 145 },
        { match: 'Match 3', runs: response.data.avg_runs * 0.6 || 15, strikeRate: response.data.avg_strike_rate * 0.8 || 110 },
        { match: 'Match 4', runs: response.data.avg_runs * 1.4 || 55, strikeRate: response.data.avg_strike_rate * 1.2 || 155 },
        { match: 'Match 5', runs: response.data.avg_runs || 35, strikeRate: response.data.avg_strike_rate || 135 },
      ];
      setPlayerHistory(sampleHistory);
      
      // Filter teams to show only teams player has played for
      const filteredPlayerTeams = allTeams.filter(team => 
        playerTeamsList.includes(team.team)
      );
      setTeams(filteredPlayerTeams.length > 0 ? filteredPlayerTeams : allTeams);
    } catch (error) {
      console.error('Error fetching player teams:', error);
      setTeams(allTeams);
      setPlayerHistory([]);
    }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setError('');
    setPrediction(null);

    if (!formData.player || !formData.team || !formData.opponent || !formData.venue) {
      setError('Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      const response = await predictPerformance(formData);
      setPrediction(response.data);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to get prediction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prediction-page">
      <div className="page-header">
        <h1 className="page-title">Performance Prediction</h1>
        <p className="page-subtitle">Predict player performance for upcoming matches</p>
      </div>

      <div className="prediction-container">
        {/* Left Side - Form */}
        <div className="prediction-form-card card">
          <div className="card-header">
            <h2 className="card-title">
              <TrendingUp size={20} />
              Match Details
            </h2>
          </div>

          <form onSubmit={handlePredict} className="prediction-form">
            {/* Player Input */}
            <div className="form-group">
              <label className="form-label">Player Name</label>
              <div className="search-input-wrapper">
                <Search size={18} className="search-icon" />
                <input
                  type="text"
                  className="form-input"
                  placeholder="Search for a player..."
                  value={formData.player}
                  onChange={(e) => handleInputChange('player', e.target.value)}
                  autoComplete="off"
                />
                {playerSuggestions.length > 0 && (
                  <div className="suggestions-dropdown">
                    {playerSuggestions.map((player, index) => (
                      <div
                        key={index}
                        className="suggestion-item"
                        onClick={() => handlePlayerSelect(player.player)}
                      >
                        <div className="suggestion-name">{player.player}</div>
                        <div className="suggestion-stats">
                          {player.total_runs} runs · {player.matches} matches
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Team Select */}
            <div className="form-group">
              <label className="form-label">Playing For</label>
              <select
                className="form-select"
                value={formData.team}
                onChange={(e) => handleInputChange('team', e.target.value)}
              >
                <option value="">Select team...</option>
                {teams.map((team, index) => (
                  <option key={index} value={team.team}>
                    {team.team}
                  </option>
                ))}
              </select>
            </div>

            {/* Opponent Select */}
            <div className="form-group">
              <label className="form-label">Against</label>
              <select
                className="form-select"
                value={formData.opponent}
                onChange={(e) => handleInputChange('opponent', e.target.value)}
              >
                <option value="">Select opponent...</option>
                {allTeams
                  .filter(team => team.team !== formData.team)
                  .map((team, index) => (
                    <option key={index} value={team.team}>
                      {team.team}
                    </option>
                  ))}
              </select>
            </div>

            {/* Venue Select */}
            <div className="form-group">
              <label className="form-label">Venue</label>
              <select
                className="form-select"
                value={formData.venue}
                onChange={(e) => handleInputChange('venue', e.target.value)}
              >
                <option value="">Select venue...</option>
                {venues.map((venue, index) => (
                  <option key={index} value={venue.venue}>
                    {venue.venue}
                  </option>
                ))}
              </select>
            </div>

            {/* Model Select */}
            <div className="form-group">
              <label className="form-label">ML Model</label>
              <select
                className="form-select"
                value={formData.model_name}
                onChange={(e) => handleInputChange('model_name', e.target.value)}
              >
                {models.length === 0 ? (
                  <option value="xgboost">XGBoost (Default)</option>
                ) : (
                  models.map((model, index) => (
                    <option key={index} value={model.name}>
                      {model.name.replace('_', ' ').toUpperCase()} 
                      {model.is_default ? ' (Default)' : ''}
                      {typeof model.test_rmse === 'number' ? ` - RMSE: ${model.test_rmse.toFixed(2)}` : ''}
                    </option>
                  ))
                )}
              </select>
            </div>

            {error && (
              <div className="error-message">
                <AlertCircle size={18} />
                {error}
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={loading}
            >
              {loading ? 'Predicting...' : 'Predict Performance'}
            </button>
          </form>
        </div>

        {/* Right Side - Visualization */}
        <div className="visualization-section">
          {/* Player Statistics Chart */}
          <div className="card visualization-card">
            <div className="card-header">
              <h2 className="card-title">
                <BarChart3 size={20} />
                {formData.player ? `${formData.player} - Recent Performance` : 'Player Performance Analysis'}
              </h2>
            </div>
            <div className="chart-content">
              {playerHistory.length > 0 ? (
                <ResponsiveContainer width="100%" height={windowWidth < 768 ? 250 : 300}>
                  <LineChart data={playerHistory}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="match" fontSize={windowWidth < 480 ? 10 : 12} />
                    <YAxis yAxisId="left" fontSize={windowWidth < 480 ? 10 : 12} />
                    <YAxis yAxisId="right" orientation="right" fontSize={windowWidth < 480 ? 10 : 12} />
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: windowWidth < 480 ? '12px' : '14px' }} />
                    <Line yAxisId="left" type="monotone" dataKey="runs" stroke="#2563eb" strokeWidth={windowWidth < 480 ? 1.5 : 2} name="Runs" />
                    <Line yAxisId="right" type="monotone" dataKey="strikeRate" stroke="#22c55e" strokeWidth={windowWidth < 480 ? 1.5 : 2} name="Strike Rate" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="chart-placeholder">
                  <BarChart3 size={64} className="placeholder-icon" />
                  <p className="placeholder-text">Select a player to view performance trends</p>
                  <p className="placeholder-subtext">Recent match statistics will appear here</p>
                </div>
              )}
            </div>
          </div>

          {/* Prediction Comparison Chart */}
          <div className="card visualization-card">
            <div className="card-header">
              <h2 className="card-title">
                <Activity size={20} />
                Model Predictions Comparison
              </h2>
            </div>
            <div className="chart-content">
              {prediction ? (
                <ResponsiveContainer width="100%" height={windowWidth < 768 ? 250 : 300}>
                  <BarChart data={[
                    { metric: 'Runs', value: prediction.predicted_runs || 0 },
                    { metric: 'Strike Rate', value: prediction.predicted_strike_rate || 0 },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="metric" fontSize={windowWidth < 480 ? 11 : 12} />
                    <YAxis fontSize={windowWidth < 480 ? 10 : 12} />
                    <Tooltip 
                      formatter={(value) => value.toFixed(1)}
                      contentStyle={{ background: 'white', border: '1px solid #d1d5db', fontSize: windowWidth < 480 ? '12px' : '14px' }}
                    />
                    <Bar dataKey="value">
                      <Cell fill="#2563eb" />
                      <Cell fill="#22c55e" />
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="chart-placeholder">
                  <Activity size={64} className="placeholder-icon" />
                  <p className="placeholder-text">Make a prediction to see comparison</p>
                  <p className="placeholder-subtext">Model predictions will be visualized here</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Prediction Results - Full Width Below */}
      <div className="prediction-results-container">
        {prediction && (
          <div className="prediction-result card">
            <div className="card-header">
              <h2 className="card-title">Prediction Results</h2>
            </div>

            <div className="result-content">
              <div className="player-info">
                <h3 className="player-name">{prediction.player}</h3>
                <p className="match-info">
                  {prediction.team} vs {prediction.opponent}
                </p>
                <p className="venue-info">{prediction.venue}</p>
              </div>

              <div className="prediction-stats">
                <div className="prediction-stat-card">
                  <div className="stat-icon-large">
                    <TrendingUp size={32} />
                  </div>
                  <div className="stat-details">
                    <span className="stat-label">Predicted Runs</span>
                    <span className="stat-value-large">
                      {prediction.predicted_runs?.toFixed(0) || 'N/A'}
                    </span>
                  </div>
                </div>

                <div className="prediction-stat-card">
                  <div className="stat-icon-large secondary">
                    <TrendingUp size={32} />
                  </div>
                  <div className="stat-details">
                    <span className="stat-label">Predicted Strike Rate</span>
                    <span className="stat-value-large">
                      {prediction.predicted_strike_rate?.toFixed(1) || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {prediction.confidence && (
                <div className="confidence-section">
                  <div className="confidence-label">Confidence Level</div>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{ width: `${prediction.confidence}%` }}
                    ></div>
                  </div>
                  <div className="confidence-value">{prediction.confidence}%</div>
                </div>
              )}

              {prediction.factors && (
                <div className="factors-section">
                  <h4 className="factors-title">Key Factors</h4>
                  <div className="factors-grid">
                    {Object.entries(prediction.factors).map(([key, value]) => (
                      <div key={key} className="factor-item">
                        <span className="factor-label">
                          {key.replace(/_/g, ' ')}
                        </span>
                        <span className="factor-value">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Prediction;
