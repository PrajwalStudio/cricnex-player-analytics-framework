import React, { useState, useEffect } from 'react';
import { Users, TrendingUp, Trophy, Activity } from 'lucide-react';
import StatCard from '../components/StatCard';
import { getStatsSummary, getTopRunScorers, getModels } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Dashboard.css';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [topPlayers, setTopPlayers] = useState([]);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    fetchDashboardData();
    
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, playersRes, modelsRes] = await Promise.all([
        getStatsSummary(),
        getTopRunScorers({ limit: 10 }),
        getModels()
      ]);

      setStats(statsRes.data);
      setTopPlayers(playersRes.data.leaderboard || []);
      setModels(modelsRes.data.models || []);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Dashboard</h1>
        <p className="dashboard-subtitle">Cricket Performance Analytics System</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <StatCard
          icon={Users}
          title="Total Players"
          value={stats?.total_players || 0}
          subtitle="Active players"
          color="primary"
        />
        <StatCard
          icon={Trophy}
          title="Total Matches"
          value={stats?.total_matches || 0}
          subtitle="Analyzed matches"
          color="success"
        />
        <StatCard
          icon={TrendingUp}
          title="Avg Runs"
          value={stats?.avg_runs_per_match || 0}
          subtitle="Per match"
          color="warning"
        />
        <StatCard
          icon={Activity}
          title="Avg Strike Rate"
          value={stats?.avg_strike_rate || 0}
          subtitle="Overall"
          color="danger"
        />
      </div>

      {/* Models Section - All 4 Models */}
      <div className="models-section">
        <div className="section-header">
          <h2 className="section-title">
            <Activity size={24} />
            ML Models Performance
          </h2>
          <p className="section-subtitle">Comparison of all trained models</p>
        </div>
        <div className="models-grid">
          {models.map((model, index) => (
            <div key={index} className="model-card">
              <div className="model-card-header">
                <h3 className="model-name">{model.name.toUpperCase()}</h3>
              </div>
              <div className="model-metrics">
                <div className="model-metric-item">
                  <span className="metric-label">RMSE</span>
                  <span className="metric-value">
                    {typeof model.test_rmse === 'number' ? model.test_rmse.toFixed(2) : 'N/A'}
                  </span>
                </div>
                <div className="model-metric-item">
                  <span className="metric-label">MAE</span>
                  <span className="metric-value">
                    {typeof model.test_mae === 'number' ? model.test_mae.toFixed(2) : 'N/A'}
                  </span>
                </div>
                <div className="model-metric-item">
                  <span className="metric-label">R² Score</span>
                  <span className="metric-value">
                    {typeof model.test_r2 === 'number' ? model.test_r2.toFixed(3) : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content - Horizontal Layout */}
      <div className="dashboard-main-content">
        {/* Top Run Scorers Chart */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">
              <Trophy size={20} />
              Top 10 Run Scorers
            </h2>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={windowWidth < 768 ? 300 : 400}>
              <BarChart data={topPlayers}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="player" 
                  angle={windowWidth < 768 ? -45 : 0} 
                  textAnchor={windowWidth < 768 ? "end" : "middle"} 
                  height={windowWidth < 768 ? 100 : 70}
                  fontSize={windowWidth < 480 ? 9 : 11}
                  interval={0}
                />
                <YAxis fontSize={windowWidth < 480 ? 10 : 12} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: windowWidth < 480 ? '12px' : '14px' }} />
                <Bar dataKey="total_runs" fill="#2563eb" name="Total Runs" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Quick Stats</h3>
          </div>
          <div className="quick-stats">
            <div className="quick-stat-item">
              <span className="quick-stat-label">Total Runs</span>
              <span className="quick-stat-value">{stats?.total_runs?.toLocaleString()}</span>
            </div>
            <div className="quick-stat-item">
              <span className="quick-stat-label">Highest Score</span>
              <span className="quick-stat-value">{stats?.highest_score}</span>
            </div>
            <div className="quick-stat-item">
              <span className="quick-stat-label">Total Teams</span>
              <span className="quick-stat-value">{stats?.total_teams}</span>
            </div>
            <div className="quick-stat-item">
              <span className="quick-stat-label">Total Venues</span>
              <span className="quick-stat-value">{stats?.total_venues}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">System Status</h3>
          </div>
          <div className="system-status">
            <div className="status-item">
              <div className="status-indicator active"></div>
              <div>
                <p className="status-label">API Status</p>
                <p className="status-value">Connected</p>
              </div>
            </div>
            <div className="status-item">
              <div className="status-indicator active"></div>
              <div>
                <p className="status-label">Model Status</p>
                <p className="status-value">Active</p>
              </div>
            </div>
            <div className="status-item">
              <div className="status-indicator active"></div>
              <div>
                <p className="status-label">Database</p>
                <p className="status-value">{stats?.total_matches} Matches Loaded</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
