import React from "react";
import { Link } from "react-router-dom";
import { UserIcon } from "@heroicons/react/solid"; // Importing profile icon

const Header = () => {
  return (
    <header className="bg-gray-900 shadow-md py-4 sticky top-0 z-50">
      {/* Sticky Navbar with shadow */}
      <div className="container mx-auto px-4">
        {/* Single Row for Desktop */}
        <div className="flex justify-between items-center">
          {/* Left: Logo */}
          <Link to="/" className="flex items-center">
            <img
              src={require("../images/sampleicon.png")}
              alt="Icon"
              className="h-8 w-8"
            />
          </Link>

          {/* Center: Navigation Links */}
          <div className="flex items-center space-x-8 mx-auto">
            <Link
              to="/"
              className="text-gray-300 hover:text-white hover:underline"
            >
              Home
            </Link>
            <Link
              to="/dashboard"
              className="text-gray-300 hover:text-white hover:underline"
            >
              Dashboard
            </Link>
            <Link
              to="/subscription-manager"
              className="text-gray-300 hover:text-white hover:underline"
            >
              Subscription Manager
            </Link>
          </div>

          {/* Right: Profile Icon */}
          <div className="flex items-center">
            <Link to="/login">
              <UserIcon className="h-6 w-6 text-gray-300 hover:text-white" />
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;