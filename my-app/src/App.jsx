import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import LandingPage from './pages/LandingPage'
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import SubscriptionManager from './pages/SubscriptionManager';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';

// Inside the Routes component

function App() {
  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/subscriptions" element={<SubscriptionManager />} />
      </Routes>
      <Footer />
    </Router>
  );
}

export default App;
