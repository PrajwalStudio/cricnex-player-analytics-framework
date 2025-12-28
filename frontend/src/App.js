import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Prediction from './pages/Prediction';
import Players from './pages/Players';
import Leaderboard from './pages/Leaderboard';
import Teams from './pages/Teams';
import Analytics from './pages/Analytics';
import './App.css';

function App() {
  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/predict" element={<Prediction />} />
          <Route path="/players" element={<Players />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/teams" element={<Teams />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
