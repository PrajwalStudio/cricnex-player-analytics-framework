import React, { useState, useEffect, useCallback } from 'react';
import { Trophy, TrendingUp, Target } from 'lucide-react';
import { getTopRunScorers, getTopStrikeRates, getTopAverages } from '../services/api';
import './Leaderboard.css';

const Leaderboard = () => {
  const [activeTab, setActiveTab] = useState('runs');
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLeaderboard = useCallback(async () => {
    try {
      setLoading(true);
      let response;
      
      switch (activeTab) {
        case 'runs':
          response = await getTopRunScorers({ limit: 50 });
          break;
        case 'strikeRate':
          response = await getTopStrikeRates({ limit: 50 });
          break;
        case 'average':
          response = await getTopAverages({ limit: 50, min_matches: 20 });
          break;
        default:
          response = await getTopRunScorers({ limit: 50 });
      }
      
      const data = response.data.leaderboard || [];
      setLeaderboard(data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  const tabs = [
    { id: 'runs', label: 'Top Run Scorers', icon: Trophy },
    { id: 'strikeRate', label: 'Best Strike Rates', icon: TrendingUp },
    { id: 'average', label: 'Best Averages', icon: Target }
  ];

  const getMedalClass = (rank) => {
    if (rank === 1) return 'gold';
    if (rank === 2) return 'silver';
    if (rank === 3) return 'bronze';
    return '';
  };

  return (
    <div className="leaderboard-page">
      <div className="page-header">
        <h1 className="page-title">Leaderboard</h1>
        <p className="page-subtitle">Top performing players across all metrics</p>
      </div>

      <div className="card">
        <div className="tabs-container">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon size={18} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="spinner"></div>
            <p>Loading leaderboard...</p>
          </div>
        ) : (
          <div className="leaderboard-table">
            <div className="table-header">
              <div className="th-rank">Rank</div>
              <div className="th-player">Player</div>
              <div className="th-stat">Matches</div>
              {activeTab === 'runs' && (
                <>
                  <div className="th-stat">Total Runs</div>
                  <div className="th-stat">Average</div>
                  <div className="th-stat">Highest</div>
                </>
              )}
              {activeTab === 'strikeRate' && (
                <>
                  <div className="th-stat">Strike Rate</div>
                  <div className="th-stat">Total Runs</div>
                  <div className="th-stat">Average</div>
                </>
              )}
              {activeTab === 'average' && (
                <>
                  <div className="th-stat">Average</div>
                  <div className="th-stat">Total Runs</div>
                  <div className="th-stat">Strike Rate</div>
                </>
              )}
            </div>

            <div className="table-body">
              {leaderboard.map((player, index) => (
                <div key={index} className={`table-row ${getMedalClass(player.rank || index + 1)}`}>
                  <div className="td-rank">
                    <div className="rank-badge">
                      #{player.rank || index + 1}
                    </div>
                  </div>
                  <div className="td-player">
                    <div className="player-avatar-small">
                      {player.player?.substring(0, 2).toUpperCase()}
                    </div>
                    <span className="player-name-table">{player.player}</span>
                  </div>
                  <div className="td-stat">{player.matches}</div>
                  
                  {activeTab === 'runs' && (
                    <>
                      <div className="td-stat highlighted">{player.total_runs}</div>
                      <div className="td-stat">{player.avg_runs?.toFixed(1)}</div>
                      <div className="td-stat">{player.highest_score}</div>
                    </>
                  )}
                  {activeTab === 'strikeRate' && (
                    <>
                      <div className="td-stat highlighted">{(player.avg_strike_rate || player.strike_rate)?.toFixed(2)}</div>
                      <div className="td-stat">{player.total_runs}</div>
                      <div className="td-stat">{player.avg_runs?.toFixed(1)}</div>
                    </>
                  )}
                  {activeTab === 'average' && (
                    <>
                      <div className="td-stat highlighted">{(player.avg_runs || player.average)?.toFixed(2)}</div>
                      <div className="td-stat">{player.total_runs}</div>
                      <div className="td-stat">{(player.avg_strike_rate || player.strike_rate)?.toFixed(2)}</div>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Leaderboard;
