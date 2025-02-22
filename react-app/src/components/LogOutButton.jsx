import React from "react";
import { useNavigate } from "react-router-dom";

const LogoutButton = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login"); 
  };

  return (
    <button
      onClick={handleLogout}
      className="bg-red-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-red-700 transition duration-300"
    >
      Logout
    </button>
  );
};

export default LogoutButton;