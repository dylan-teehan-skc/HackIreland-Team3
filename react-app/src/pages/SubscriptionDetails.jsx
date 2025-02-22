import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import "../index.css"; 

const SubscriptionDetails = () => {
  const { id } = useParams(); // Get subscription ID from URL

  // Placeholder values (Replace with API data)
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

  // Uncomment and replace with API call
  /*
  useEffect(() => {
    fetch(`/api/subscription/${id}`)
      .then((response) => response.json())
      .then((data) => setSubscriptionData(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, [id]);
  */

  return (
    <div className="subscription-page">
      {/* Header */}
      <header className="subscription-header">{subscriptionData.serviceName}</header>

      {/* Main Content Grid */}
      <div className="subscription-grid">
        <div className="subscription-card large">
          <h2>Payments Log</h2>
          <ul className="payment-list">
            {subscriptionData.paymentsLog.map((log, index) => (
              <li key={index}>
                {log.date}: <span className="amount">${log.amount}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="subscription-card">
          <h2>Who is Paying?</h2>
          <p>{subscriptionData.activeUsers}</p>
        </div>

        <div className="subscription-card">
          <h2>Total Spent</h2>
          <p className="amount">${subscriptionData.totalSpent}</p>
        </div>

        <div className="subscription-card">
          <h2>Upcoming Payment</h2>
          <p>Next Payment: <span className="highlight">{subscriptionData.nextPaymentDate}</span></p>
        </div>
      </div>

      {/* Deactivate Subscription */}
      <button className="deactivate-button">Deactivate Subscription</button>
    </div>
  );
};

export default SubscriptionDetails;
