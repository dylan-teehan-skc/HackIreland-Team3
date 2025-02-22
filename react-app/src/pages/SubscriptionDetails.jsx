import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import "../index.css";

const SubscriptionDetails = () => {
  const { id } = useParams();

  const [subscriptionData, setSubscriptionData] = useState({
    serviceName: "Your Netflix Subscription",
    paymentsLog: [
      { date: "2024-02-01", amount: 15.99 },
      { date: "2024-01-01", amount: 15.99 },
      { date: "2023-12-01", amount: 15.99 },
    ],
    activeUsers: "Shared with 2 others",
    totalSpent: 191.88,
    nextPaymentDate: "2024-03-01",
  });

  /*
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-4">Payments Log</h2>
          <ul className="space-y-2">
            {subscriptionData.paymentsLog.map((log, index) => (
              <li key={index} className="flex justify-between">
                <span>{log.date}</span>
                <span className="text-purple-400">${log.amount}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-4">Who is Paying?</h2>
          <p className="text-gray-300">{subscriptionData.activeUsers}</p>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-4">Total Spent</h2>
          <p className="text-3xl text-purple-400">${subscriptionData.totalSpent}</p>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-4">Upcoming Payment</h2>
          <p className="text-gray-300">
            Next Payment: <span className="text-purple-400">{subscriptionData.nextPaymentDate}</span>
          </p>
        </div>
      </div>

      <button className="mt-8 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-3 px-8 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50">
        Deactivate Subscription
      </button>
    </div>
  );
};

export default SubscriptionDetails;