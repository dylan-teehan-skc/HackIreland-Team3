import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const Account = () => {
  const [userDetails, setUserDetails] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchUserDetails = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const response = await fetch("http://localhost:8000/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch user details");
        }

        const data = await response.json();
        setUserDetails(data);
      } catch (err) {
        setError(err.message || "An error occurred. Please try again.");
      }
    };

    fetchUserDetails();
  }, []);

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  if (!userDetails) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col justify-center items-center p-6">
      <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          Your Account
        </h1>
        <div className="space-y-4">
          <p><strong>Email:</strong> {userDetails.email}</p>
          <p><strong>First Name:</strong> {userDetails.first_name}</p>
          <p><strong>Last Name:</strong> {userDetails.last_name}</p>
          <p><strong>Date of Birth:</strong> {userDetails.date_of_birth}</p>
          <p><strong>Address:</strong> {userDetails.address_line1}, {userDetails.city}, {userDetails.state}, {userDetails.postal_code}, {userDetails.country}</p>
          <p><strong>Phone Number:</strong> {userDetails.phone_number}</p>
          
          <Link 
            to="/add-card" 
            className="mt-4 block w-full text-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Add Payment Card
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Account; 