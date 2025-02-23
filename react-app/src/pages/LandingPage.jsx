import React from "react";
import { Link } from "react-router-dom";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col justify-center items-center p-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-gray-900 to-gray-900 opacity-75 -z-10"></div>

      <div className="text-center max-w-2xl relative z-10">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent animate-gradient">
          Take Control of Your Subscriptions
        </h1>

        <p className="text-lg md:text-xl text-gray-300 mb-12 leading-relaxed">
          SubClub helps you manage, track, and split recurring expenses with ease.
          Never miss a payment again!
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/dashboard"
            className="relative bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50"
          >
            <span className="relative z-10">Go to Dashboard</span>
            <span className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg opacity-0 hover:opacity-100 transition-opacity duration-300"></span>
          </Link>
          <Link
            to="/subscriptions"
            className="relative bg-transparent border-2 border-purple-600 hover:border-purple-700 text-purple-600 hover:text-purple-700 font-semibold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50"
          >
            <span className="relative z-10">Manage Subscriptions</span>
            <span className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg opacity-0 hover:opacity-10 transition-opacity duration-300"></span>
          </Link>
        </div>
      </div>

      <div className="absolute w-64 h-64 bg-purple-600 rounded-full opacity-20 blur-3xl animate-blob animation-delay-2000 -top-32 -left-32"></div>
      <div className="absolute w-64 h-64 bg-pink-600 rounded-full opacity-20 blur-3xl animate-blob animation-delay-4000 -bottom-32 -right-32"></div>
    </div>
  );
};

export default LandingPage;