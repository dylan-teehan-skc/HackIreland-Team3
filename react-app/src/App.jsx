import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import SubscriptionManager from "./pages/SubscriptionManager";
import SubscriptionDetails from "./pages/SubscriptionDetails";
import SplitSubscription from "./pages/SplitSubscription";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/subscriptions" element={<SubscriptionManager />} />
            <Route path="/split-subscription" element={<SplitSubscription />} />
            <Route path="/subscription/:id" element={<SubscriptionDetails />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
