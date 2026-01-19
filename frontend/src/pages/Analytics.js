import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Activity } from 'lucide-react';
import { getRecentForm, getPlayerMatchups } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Analytics.css';

const Analytics = () => {
  const [recentForm, setRecentForm] = useState([]);
  const [matchupData, setMatchupData] = useState(null);
  const [playerQuery, setPlayerQuery] = useState('');
  const [opponentQuery, setOpponentQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [matchupLoading, setMatchupLoading] = useState(false);
  const [matchupError, setMatchupError] = useState('');
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    fetchRecentForm();
    
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const fetchRecentForm = async () => {
    try {
      setLoading(true);
      const response = await getRecentForm({ days: 30, limit: 10 });
      const formData = response.data.form || [];
      setRecentForm(formData);
    } catch (error) {
      console.error('Error fetching recent form:', error);
      setRecentForm([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchMatchupData = async () => {
    if (!playerQuery || !opponentQuery) return;

    try {
      setMatchupLoading(true);
      setMatchupError('');
      setMatchupData(null);
      const response = await getPlayerMatchups({
        player: playerQuery.trim(),
        opponent: opponentQuery.trim()
      });
      setMatchupData(response.data);
      
      // Show message if no matches found
      if (response.data.matches === 0) {
        setMatchupError('No matchup data found for this combination');
      }
    } catch (error) {
      console.error('Error fetching matchup data:', error);
      setMatchupError(error.response?.data?.error || 'Failed to fetch matchup data. Please try again.');
    } finally {
      setMatchupLoading(false);
    }
  };

  return (
    <div className="analytics-page">
      <div className="page-header">
        <h1 className="page-title">Analytics</h1>
        <p className="page-subtitle">Advanced performance analytics and insights</p>
      </div>

      {/* Recent Form Chart */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <TrendingUp size={20} />
            Recent Form Trends (Last 30 Days)
          </h2>
        </div>
        
        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
          </div>
        ) : recentForm.length === 0 ? (
          <div style={{
            padding: '40px',
            textAlign: 'center',
            color: '#666'
          }}>
            <p>No recent form data available</p>
          </div>
        ) : (
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={windowWidth < 768 ? 300 : 400}>
              <LineChart data={recentForm}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="player" 
                  angle={windowWidth < 768 ? -45 : 0} 
                  textAnchor={windowWidth < 768 ? "end" : "middle"} 
                  height={windowWidth < 768 ? 90 : 60}
                  fontSize={windowWidth < 480 ? 9 : 11}
                  interval={0}
                />
                <YAxis fontSize={windowWidth < 480 ? 10 : 12} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: windowWidth < 480 ? '12px' : '14px' }} />
                <Line 
                  type="monotone" 
                  dataKey="avg_runs" 
                  stroke="#2563eb" 
                  strokeWidth={windowWidth < 480 ? 1.5 : 2}
                  name="Avg Runs"
                  dot={{ r: windowWidth < 480 ? 3 : 4 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="avg_strike_rate" 
                  stroke="#22c55e" 
                  strokeWidth={windowWidth < 480 ? 1.5 : 2}
                  name="Strike Rate"
                  dot={{ r: windowWidth < 480 ? 3 : 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Player vs Team Matchup Analysis */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            <Activity size={20} />
            Player vs Team Matchup Analysis
          </h2>
        </div>

        <div className="matchup-form">
          <div className="form-group">
            <label className="form-label">Player Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., V Kohli"
              value={playerQuery}
              onChange={(e) => setPlayerQuery(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Opponent Team</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., Mumbai Indians"
              value={opponentQuery}
              onChange={(e) => setOpponentQuery(e.target.value)}
            />
          </div>

          <button
            className="btn btn-primary"
            onClick={fetchMatchupData}
            disabled={!playerQuery || !opponentQuery || matchupLoading}
          >
            <BarChart3 size={18} />
            {matchupLoading ? 'Analyzing...' : 'Analyze Matchup'}
          </button>
        </div>

        {matchupLoading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Analyzing matchup data...</p>
          </div>
        )}

        {matchupError && (
          <div className="error-message" style={{
            padding: '20px',
            backgroundColor: '#fee',
            color: '#c33',
            borderRadius: '8px',
            margin: '20px 0',
            textAlign: 'center'
          }}>
            {matchupError}
          </div>
        )}

        {matchupData && matchupData.matches > 0 && (
          <div className="matchup-results">
            <div className="matchup-header">
              <h3 className="matchup-title">
                {matchupData.player} vs {matchupData.opponent}
              </h3>
              <p className="matchup-matches">{matchupData.matches} Matches</p>
            </div>

            <div className="matchup-stats-grid">
              <div className="matchup-stat-card">
                <div className="matchup-stat-label">Total Runs</div>
                <div className="matchup-stat-value">{matchupData.total_runs}</div>
              </div>

              <div className="matchup-stat-card">
                <div className="matchup-stat-label">Average Runs</div>
                <div className="matchup-stat-value">{matchupData.avg_runs?.toFixed(1)}</div>
              </div>

              <div className="matchup-stat-card">
                <div className="matchup-stat-label">Highest Score</div>
                <div className="matchup-stat-value">{matchupData.highest_score}</div>
              </div>

              <div className="matchup-stat-card">
                <div className="matchup-stat-label">Avg Strike Rate</div>
                <div className="matchup-stat-value">{matchupData.avg_strike_rate?.toFixed(1)}</div>
              </div>
            </div>

            {matchupData.performances && matchupData.performances.length > 0 && (
              <div className="performances-section">
                <h4 className="performances-title">
                  Recent Performance History 
                  {matchupData.performances.length > 0 && (
                    <span style={{ fontSize: '0.85em', fontWeight: 'normal', color: '#666', marginLeft: '10px' }}>
                      (Showing {Math.min(10, matchupData.performances.length)} most recent)
                    </span>
                  )}
                </h4>
                <div className="performances-list">
                  {matchupData.performances.slice(0, 10).map((perf, index) => (
                    <div key={index} className="performance-item">
                      <div className="perf-runs">{perf.runs_scored}</div>
                      <div className="perf-details">
                        <div className="perf-venue">{perf.venue}</div>
                        <div className="perf-sr">SR: {perf.strike_rate?.toFixed(1)}</div>
                      </div>
                      <div className="perf-date">
                        {new Date(perf.date).toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'short', 
                          day: 'numeric' 
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Analytics;
