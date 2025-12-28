import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  TrendingUp, 
  Users, 
  Trophy, 
  Shield, 
  BarChart3,
  Menu,
  X
} from 'lucide-react';
import './Layout.css';

const Layout = ({ children }) => {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const menuItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/predict', icon: TrendingUp, label: 'Predict' },
    { path: '/players', icon: Users, label: 'Players' },
    { path: '/leaderboard', icon: Trophy, label: 'Leaderboard' },
    { path: '/teams', icon: Shield, label: 'Teams' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
  ];

  return (
    <div className="layout">
      {/* Horizontal Navbar */}
      <header className="navbar">
        <div className="navbar-container">
          <div className="navbar-left">
            <div className="logo">
              <div className="logo-icon">CN</div>
              <span className="logo-text">CricNex</span>
            </div>
          </div>

          <nav className={`navbar-nav ${sidebarOpen ? 'open' : ''}`}>
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`nav-item ${isActive ? 'active' : ''}`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="navbar-right">
            <button className="mobile-menu-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main">
        <div className="content">
          {children}
        </div>
      </main>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div className="overlay" onClick={() => setSidebarOpen(false)}></div>
      )}
    </div>
  );
};

export default Layout;
