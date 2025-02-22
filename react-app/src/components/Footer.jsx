import React from "react";
import { Link } from "react-router-dom";
import "../index.css";

const Footer = () => {
  return (
    <footer className="bg-gray-900 border-t border-gray-800 py-8">
      <nav className="container mx-auto flex flex-col items-center space-y-4">
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
        <p className="text-gray-500 text-sm">
          &copy; {new Date().getFullYear()} SubHub. All rights reserved.
        </p>
      </nav>
    </footer>
  );
};

export default Footer;