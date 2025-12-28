import React from 'react';
import './StatCard.css';

const StatCard = ({ icon: Icon, title, value, subtitle, trend, color }) => {
  return (
    <div className={`stat-card ${color || ''}`}>
      <div className="stat-icon">
        <Icon size={24} />
      </div>
      <div className="stat-content">
        <p className="stat-title">{title}</p>
        <h3 className="stat-value">{value}</h3>
        {subtitle && <p className="stat-subtitle">{subtitle}</p>}
        {trend && (
          <div className={`stat-trend ${trend > 0 ? 'positive' : 'negative'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </div>
        )}
      </div>
    </div>
  );
};

export default StatCard;
