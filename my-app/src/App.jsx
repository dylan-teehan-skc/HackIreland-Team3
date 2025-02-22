import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import './App.css';
import LandingPage from './pages/LandingPage'
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import SubscriptionManager from './pages/SubscriptionManager';
import Footer from './components/Footer';
import SubscriptionDetails from "./pages/SubscriptionDetails";
import SplitSubscription from "./pages/SplitSubscription";

function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/subscriptions" element={<SubscriptionManager />} />
        <Route path="/splitsubscription" element={<SplitSubscription />} />
        <Route path="/subscription/:id" element={<SubscriptionDetails />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  );
}

export default App;
