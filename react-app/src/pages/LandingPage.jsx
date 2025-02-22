import React from "react";
import { Link } from "react-router-dom";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col justify-center items-center p-6">
      {/* Main Content */}
      <div className="text-center max-w-2xl">
        {/* Title */}
        <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          Take Control of Your Subscriptions
        </h1>

        {/* Subtitle */}
        <p className="text-lg text-gray-300 mb-8">
          SubClub helps you manage, track, and split recurring expenses with ease.
          Never miss a payment again!
        </p>

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/dashboard"
            className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-300 transform hover:scale-105"
          >
            Go to Dashboard
          </Link>
          <Link
            to="/subscriptions"
            className="bg-transparent border-2 border-purple-600 hover:border-purple-700 text-purple-600 hover:text-purple-700 font-semibold py-3 px-6 rounded-lg transition duration-300 transform hover:scale-105"
          >
            Manage Subscriptions
          </Link>
        </div>
      </div>

      {/* Optional: Add a decorative gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-800 to-gray-900 opacity-50 -z-10"></div>
    </div>
  );
};

export default LandingPage;