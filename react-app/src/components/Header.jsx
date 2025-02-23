import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "../index.css";

const Header = () => {
  const isAuthenticated = !!localStorage.getItem("access_token");
  const navigate = useNavigate();
  const [hasCard, setHasCard] = React.useState(false);

  React.useEffect(() => {
    const checkCard = async () => {
      if (isAuthenticated) {
        try {
          const token = localStorage.getItem("access_token");
          const response = await fetch("http://localhost:8000/real-cards/has-card", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          if (response.ok) {
            const data = await response.json();
            setHasCard(data.has_card);
          }
        } catch (error) {
          console.error("Error checking card status:", error);
        }
      }
    };
    checkCard();
  }, [isAuthenticated]);

  const handleSignOut = () => {
    localStorage.removeItem("access_token");
    navigate("/");
  };

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
          {isAuthenticated && (
            <Link
              to="/groups"
              className="text-gray-300 hover:text-white font-semibold text-lg transition duration-300 hover:scale-105"
            >
              Groups
            </Link>
          )}
        </div>
        <div className="flex space-x-6">
          {isAuthenticated ? (
            <>
              {!hasCard && (
                <Link to="/add-card" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-2 px-6 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50">
                  Add a Card
                </Link>
              )}
              <Link to="/account" className="bg-transparent border-2 border-purple-600 text-purple-600 hover:text-white hover:bg-purple-600 font-semibold py-2 px-6 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50">
                Your Account
              </Link>
            </>
          ) : (
            <>
              <Link to="/login" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-2 px-6 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50">
                Sign In
              </Link>
              <Link to="/signup" className="bg-transparent border-2 border-purple-600 text-purple-600 hover:text-white hover:bg-purple-600 font-semibold py-2 px-6 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header;