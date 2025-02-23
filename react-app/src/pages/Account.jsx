import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const Account = () => {
  const [userDetails, setUserDetails] = useState(null);
  const [error, setError] = useState("");
  const [hasCard, setHasCard] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("access_token");
      
      // Fetch user details
      try {
        const userResponse = await fetch("http://localhost:8000/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!userResponse.ok) {
          throw new Error("Failed to fetch user details");
        }

        const userData = await userResponse.json();
        setUserDetails(userData);
      } catch (err) {
        setError(err.message || "An error occurred. Please try again.");
      }

      // Check if user has a card
      try {
        const cardResponse = await fetch("http://localhost:8000/real-cards/has-card", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (cardResponse.ok) {
          const cardData = await cardResponse.json();
          setHasCard(cardData.has_card);
        }
      } catch (error) {
        console.error("Error checking card status:", error);
      }
    };

    fetchData();
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
        </div>
      </div>
    </div>
  );
};

export default Account; 