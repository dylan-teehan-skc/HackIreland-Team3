import React, { useEffect, useState } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import "../index.css";

const SubscriptionDetails = () => {
  const { fileId, description, amount } = useParams();
  const location = useLocation();
  const [subscriptionDetails, setSubscriptionDetails] = useState(null);
  const [totalSpent, setTotalSpent] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSubscriptionDetails = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/subscriptions/filter/${fileId}?description=${encodeURIComponent(description)}&price=${amount}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setSubscriptionDetails(data[0]);
      } catch (error) {
        console.error("Error fetching subscription details:", error);
      }
    };

    const fetchTotalSpent = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/subscriptions/specific_spent/${fileId}?description=${encodeURIComponent(description)}&price=${amount}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setTotalSpent(data.specific_spent);
      } catch (error) {
        console.error("Error fetching total spent:", error);
      }
    };

    fetchSubscriptionDetails();
    fetchTotalSpent();
  }, [fileId, description, amount]);

  useEffect(() => {
    if (location.state?.generatedInfo) {
      setLoading(false);
    }
  }, [location.state]);

  if (loading || !subscriptionDetails) {
    return <div>Loading...</div>;
  }

  const generatedInfo = location.state?.generatedInfo || {};
  const { cancellation_link, alternatives } = generatedInfo;

  const sortedDates = [...subscriptionDetails.Dates].sort((a, b) => new Date(b) - new Date(a));

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          {subscriptionDetails.Description}
        </h1>
        <div className="flex items-center">
          {cancellation_link && (
            <a href={cancellation_link} target="_blank" rel="noopener noreferrer" className="mr-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-3 px-8 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50">
              Cancel Subscription
            </a>
          )}
          <button
            onClick={() => navigate(-1)}
            className="flex items-center bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded-lg transition duration-300"
          >
            Back
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-4">Amount</h2>
          <p className="text-3xl text-purple-400">${subscriptionDetails.Amount.toFixed(2)}</p>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-4">Previous Payment Dates</h2>
          <div className="overflow-y-auto" style={{ maxHeight: '150px' }}>
            <table className="min-w-full">
              <thead>
                <tr>
                  <th className="py-2 px-4 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Date</th>
                </tr>
              </thead>
              <tbody>
                {sortedDates.map((date, index) => (
                  <tr key={index} className="border-b border-gray-700">
                    <td className="py-2 px-4 text-sm text-gray-300">{date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-4">Upcoming Payment</h2>
          <p className="text-gray-300">
            Next Payment: <span className="text-purple-400">{subscriptionDetails.Estimated_Next}</span>
          </p>
          <h2 className="text-2xl font-semibold mt-4">Total Spent</h2>
          <p className="text-3xl text-purple-400">${totalSpent.toFixed(2)}</p>
        </div>
      </div>

      {alternatives && (
        <div className="mt-8 bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-4">Alternatives</h2>
          {alternatives.map((alt, index) => (
            <div key={index} className="mb-4">
              <h3 className="text-xl font-bold text-purple-400">{alt.name}</h3>
              <p className="text-gray-300">{alt.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SubscriptionDetails;