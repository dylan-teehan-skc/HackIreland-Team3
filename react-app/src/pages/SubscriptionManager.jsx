import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import "../index.css";

const SubscriptionDetails = () => {
  const { id } = useParams();

  const [subscriptionData, setSubscriptionData] = useState({
    serviceName: "Manage Your xxx Subscription",
    paymentsLog: [
      { date: "2024-02-01", amount: 15.99 }, /* placeholders */
      { date: "2024-01-01", amount: 15.99 },
      { date: "2023-12-01", amount: 15.99 },
    ],
    activeUsers: "Shared with 2 others",
    totalSpent: 191.88,
    nextPaymentDate: "2024-03-01",
  });

  /* implement api endpoints later
  useEffect(() => {
    fetch(`/api/subscription/${id}`)
      .then((response) => response.json())
      .then((data) => setSubscriptionData(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, [id]);
  */

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
        <header className="text-4xl font-bold mb-8 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
        {subscriptionData.serviceName}
        </header>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
            <h2 className="text-2xl font-semibold mb-4">Who is Paying?</h2>
            <p className="text-gray-300">{subscriptionData.activeUsers}</p>
        </div>

        <Link to="/split" className="relative bg-transparent border-2 border-purple-600 hover:border-purple-700 text-purple-600 hover:text-purple-700 font-semibold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50"></Link>

        <button className="mt-8 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-3 px-8 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50">
        Deactivate Subscription
        </button>
    </div>
  );
};

export default SubscriptionDetails;