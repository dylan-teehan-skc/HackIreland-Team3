import React from "react";
import { Link } from "react-router-dom";
import "../index.css";

const Header = () => {
  return (
    <header className="bg-gray-900 border-b border-gray-800 py-4">
      <nav className="container mx-auto flex justify-between items-center px-6">
        <div className="flex space-x-8">
          <Link
            to="/"
            className="text-gray-300 hover:text-white font-semibold text-lg transition duration-300 hover:scale-105"
          >
            Home
          </Link>
          <Link
            to="/dashboard"
            className="text-gray-300 hover:text-white font-semibold text-lg transition duration-300 hover:scale-105"
          >
            Dashboard
          </Link>
        </div>
        <div className="flex space-x-6">
          <Link to="/login" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-2 px-6 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50">
            Sign In
          </Link>
          <Link to="/signup" className="bg-transparent border-2 border-purple-600 text-purple-600 hover:text-white hover:bg-purple-600 font-semibold py-2 px-6 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50">
            Sign Up
          </Link>
        </div>
      </nav>
    </header>
  );
};

export default Header;