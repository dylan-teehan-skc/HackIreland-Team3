import React from "react";
import { Link } from "react-router-dom";
import "../index.css";

const LandingPage = () => {
  return (
    <div className="landing-container">
      <h1 className="landing-title">Take Control of Your Subscriptions</h1>
      <p className="landing-text">
        SubClub helps you manage, track, and split recurring expenses with ease. 
        Never miss a payment again!
      </p>

      <div>
        <Link to="/dashboard" className="button primary-btn">
          Go to Dashboard
        </Link>
        <Link to="/subscriptions" className="button secondary-btn">
          Manage Subscriptions
        </Link>
      </div>
    </div>
  );
};

export default LandingPage;