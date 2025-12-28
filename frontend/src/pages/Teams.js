import React, { useState, useEffect } from 'react';
import { Shield, Users } from 'lucide-react';
import { getTeams, getTeamPlayers } from '../services/api';
import './Teams.css';

const Teams = () => {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [teamPlayers, setTeamPlayers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Function to get team logo path
  const getTeamLogo = (teamName) => {
    // Map team names to logo file names
    const logoMap = {
      'Chennai Super Kings': 'ChennaiSuperKings.png',
      'Mumbai Indians': 'MumbaiIndians.png',
      'Royal Challengers Bangalore': 'RoyalChallengersBangalore.png',
      'Royal Challengers Bengaluru': 'RoyalChallengersBangalore.png',
      'Kolkata Knight Riders': 'KolkataKnightRiders.png',
      'Delhi Capitals': 'DelhiCapitals.png',
      'Punjab Kings': 'PunjabKings.png',
      'Rajasthan Royals': 'RajasthanRoyals.png',
      'Sunrisers Hyderabad': 'SunrisesHyderbad.png',
      'Lucknow Super Giants': 'LucknowSuperGiants.png',
      'Gujarat Titans': 'GujaratTitans.png',
      'Rising Pune Supergiant': 'RisingPuneSuperGiants.png',
      'Gujarat Lions': 'GujaratLions.png',
      'Pune Warriors': 'PuneWarriorsIndia.png',
      'Pune Warriors India': 'PuneWarriorsIndia.png',
      'Kochi Tuskers Kerala': 'KochiTuskersKerala.png'
    };
    
    return logoMap[teamName] ? `/team-logos/${logoMap[teamName]}` : null;
  };

  useEffect(() => {
    fetchTeams();
  }, []);

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const response = await getTeams();
      setTeams(response.data.teams || []);
    } catch (error) {
      console.error('Error fetching teams:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTeamClick = async (team) => {
    try {
      setSelectedTeam(team);
      const response = await getTeamPlayers(team.team);
      setTeamPlayers(response.data.players || []);
    } catch (error) {
      console.error('Error fetching team players:', error);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading teams...</p>
      </div>
    );
  }

  return (
    <div className="teams-page">
      <div className="page-header">
        <h1 className="page-title">Teams</h1>
        <p className="page-subtitle">Explore IPL teams and their players</p>
      </div>

      <div className="teams-grid">
        {teams.map((team, index) => {
          const logoPath = getTeamLogo(team.team);
          return (
            <div
              key={index}
              className={`team-card ${selectedTeam?.team === team.team ? 'active' : ''}`}
              onClick={() => handleTeamClick(team)}
            >
              <div className="team-logo-container">
                {logoPath ? (
                  <img 
                    src={logoPath} 
                    alt={team.team} 
                    className="team-logo"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div className="team-icon" style={{ display: logoPath ? 'none' : 'flex' }}>
                  <Shield size={32} />
                </div>
              </div>
              <div className="team-info">
                <h3 className="team-name">{team.team}</h3>
                <div className="team-stats-mini">
                  <span>{team.matches} matches</span>
                  <span>·</span>
                  <span>Avg: {team.avg_runs?.toFixed(1)}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {selectedTeam && teamPlayers.length > 0 && (
        <div className="card team-players-section">
          <div className="card-header">
            <h2 className="card-title">
              <Users size={20} />
              {selectedTeam.team} - Squad
            </h2>
            <span className="players-count">{teamPlayers.length} Players</span>
          </div>

          <div className="players-grid">
            {teamPlayers.map((player, index) => (
              <div key={index} className="player-card-mini">
                <div className="player-avatar-mini">
                  {player.player?.substring(0, 2).toUpperCase()}
                </div>
                <div className="player-details-mini">
                  <div className="player-name-mini">{player.player}</div>
                  <div className="player-stats-inline">
                    <span>{player.total_runs} runs</span>
                    <span>·</span>
                    <span>{player.matches} matches</span>
                  </div>
                  <div className="player-avg-mini">
                    Avg: {player.avg_runs?.toFixed(1)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Teams;
