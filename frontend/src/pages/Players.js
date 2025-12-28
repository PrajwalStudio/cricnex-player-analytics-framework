import React, { useState, useEffect } from 'react';
import { Search, TrendingUp, Award, Activity, Trophy } from 'lucide-react';
import { getPlayers, getPlayerDetails } from '../services/api';
import './Players.css';

const Players = () => {
  const [players, setPlayers] = useState([]);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('total_runs');

  useEffect(() => {
    fetchPlayers();
  }, [sortBy]);

  const fetchPlayers = async () => {
    try {
      setLoading(true);
      const response = await getPlayers({ limit: 50, sortBy, order: 'desc' });
      setPlayers(response.data.players || []);
    } catch (error) {
      console.error('Error fetching players:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayerClick = async (playerName) => {
    try {
      const response = await getPlayerDetails(playerName);
      setSelectedPlayer(response.data);
    } catch (error) {
      console.error('Error fetching player details:', error);
    }
  };

  const filteredPlayers = players.filter(player =>
    player.player.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getDisplayValue = (player) => {
    switch(sortBy) {
      case 'total_runs':
        return `${player.total_runs?.toLocaleString() || 0} runs`;
      case 'matches':
        return `${player.matches || 0} matches`;
      case 'avg_runs':
        return `Avg: ${player.avg_runs?.toFixed(2) || '0.00'}`;
      case 'avg_strike_rate':
        return `SR: ${player.avg_strike_rate?.toFixed(2) || '0.00'}`;
      case 'highest_score':
        return `Best: ${player.highest_score || 0}`;
      default:
        return `${player.total_runs?.toLocaleString() || 0} runs`;
    }
  };

  return (
    <div className="players-page">
      <div className="page-header">
        <h1 className="page-title">Players</h1>
        <p className="page-subtitle">Browse and analyze player statistics</p>
      </div>

      <div className="players-container">
        {/* Players List */}
        <div className="players-list-card card">
          <div className="card-header">
            <h2 className="card-title">All Players</h2>
            <select
              className="sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="total_runs">Total Runs</option>
              <option value="matches">Matches Played</option>
              <option value="avg_runs">Average</option>
              <option value="avg_strike_rate">Strike Rate</option>
              <option value="highest_score">Highest Score</option>
            </select>
          </div>

          <div className="search-box">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search players..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          <div className="players-list">
            {loading ? (
              <div className="loading-text">Loading players...</div>
            ) : (
              filteredPlayers.map((player, index) => (
                <div
                  key={index}
                  className="player-item"
                  onClick={() => handlePlayerClick(player.player)}
                >
                  <div className="player-rank">#{index + 1}</div>
                  <div className="player-info-main">
                    <div className="player-name-item">{player.player}</div>
                    <div className="player-stats-mini">
                      <span>{player.total_runs?.toLocaleString() || 0} runs</span>
                      <span>·</span>
                      <span>{player.matches || 0} matches</span>
                    </div>
                  </div>
                  <div className="player-avg">
                    {getDisplayValue(player)}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Player Details */}
        {selectedPlayer && (
          <div className="player-details-card card">
            <div className="player-header">
              <div className="player-avatar">
                {selectedPlayer.name?.substring(0, 2).toUpperCase()}
              </div>
              <div>
                <h2 className="player-name-large">{selectedPlayer.name}</h2>
                <p className="player-matches-info">{selectedPlayer.matches} Matches</p>
              </div>
            </div>

            <div className="player-stats-grid">
              <div className="player-stat-box">
                <div className="stat-icon-player">
                  <TrendingUp size={20} />
                </div>
                <div>
                  <div className="stat-label-player">Total Runs</div>
                  <div className="stat-value-player">{selectedPlayer.total_runs?.toLocaleString() || 0}</div>
                </div>
              </div>

              <div className="player-stat-box">
                <div className="stat-icon-player">
                  <Award size={20} />
                </div>
                <div>
                  <div className="stat-label-player">Average</div>
                  <div className="stat-value-player">{selectedPlayer.average ? Number(selectedPlayer.average).toFixed(2) : '0.00'}</div>
                </div>
              </div>

              <div className="player-stat-box">
                <div className="stat-icon-player">
                  <Activity size={20} />
                </div>
                <div>
                  <div className="stat-label-player">Strike Rate</div>
                  <div className="stat-value-player">{selectedPlayer.strike_rate ? Number(selectedPlayer.strike_rate).toFixed(2) : '0.00'}</div>
                </div>
              </div>

              <div className="player-stat-box">
                <div className="stat-icon-player">
                  <Trophy size={20} />
                </div>
                <div>
                  <div className="stat-label-player">Highest Score</div>
                  <div className="stat-value-player">{selectedPlayer.highest_score || 0}</div>
                </div>
              </div>
            </div>

            <div className="player-milestones">
              <div className="milestone-item">
                <span className="milestone-label">Hundreds</span>
                <span className="milestone-value">{selectedPlayer.hundreds || 0}</span>
              </div>
              <div className="milestone-item">
                <span className="milestone-label">Fifties</span>
                <span className="milestone-value">{selectedPlayer.fifties || 0}</span>
              </div>
              <div className="milestone-item">
                <span className="milestone-label">Ducks</span>
                <span className="milestone-value">{selectedPlayer.ducks || 0}</span>
              </div>
            </div>

            {selectedPlayer.recent_form && selectedPlayer.recent_form.length > 0 && (
              <div className="recent-form-section">
                <h3 className="section-title">Recent Form</h3>
                <div className="recent-matches">
                  {selectedPlayer.recent_form.slice(0, 5).map((match, index) => (
                    <div key={index} className="recent-match-item">
                      <div className="match-runs">{match.runs_scored}</div>
                      <div className="match-details">
                        <div className="match-opponent">{match.opponent}</div>
                        <div className="match-sr">SR: {match.strike_rate?.toFixed(1)}</div>
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

export default Players;
