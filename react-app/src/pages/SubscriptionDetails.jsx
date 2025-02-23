import React, { useEffect, useState, useContext } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { SubscriptionContext } from "../context/SubscriptionContext";
import "../index.css";

const SubscriptionDetails = () => {
  const { fileId, description, amount } = useParams();
  const location = useLocation();
  const { subscriptions } = useContext(SubscriptionContext);
  const [subscriptionDetails, setSubscriptionDetails] = useState(null);
  const [totalSpent, setTotalSpent] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('');

  useEffect(() => {
    const fetchSubscriptionId = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          console.error('No access token found');
          return;
        }

        // Use the new endpoint that automatically creates subscriptions if they don't exist
        const response = await fetch(
          `http://127.0.0.1:8000/subscriptions/find_subscription?description=${encodeURIComponent(subscriptionDetails.Description)}&amount=${subscriptionDetails.Amount}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const subscription = await response.json();
        
        setSubscriptionDetails(prev => ({
          ...prev,
          id: subscription.id
        }));
        
      } catch (error) {
        console.error('Error fetching subscription:', error);
      }
    };

    // If we have subscription details but no ID, fetch/create it
    if (subscriptionDetails && !subscriptionDetails.id) {
      fetchSubscriptionId();
    }
  }, [subscriptionDetails?.Description, subscriptionDetails?.Amount]);

  useEffect(() => {
    const subscription = subscriptions.find(sub => 
      sub.Description === description && 
      sub.Amount === parseFloat(amount)
    );
    if (subscription) {
      setSubscriptionDetails(subscription);
      setLoading(false);
    }
  }, [subscriptions, description, amount]);

  useEffect(() => {
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

    fetchTotalSpent();
  }, [fileId, description, amount]);

  useEffect(() => {
    if (location.state?.generatedInfo) {
      setLoading(false);
    }
  }, [location.state]);

  useEffect(() => {
    // Fetch available groups
    const fetchGroups = async () => {
      try {
        const token = localStorage.getItem('access_token'); // Get the token from local storage
        const response = await fetch('http://127.0.0.1:8000/groups', {
          headers: {
            'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
          },
        });
        const data = await response.json();
        console.log('Fetched groups:', data); // Log the fetched groups data
        console.log(data); // Added console log to inspect the groups data
        if (Array.isArray(data)) {
          setGroups(data);
        } else {
          console.error('Unexpected data format:', data);
          setGroups([]); // Fallback to an empty array
        }
      } catch (error) {
        console.error('Error fetching groups:', error);
        setGroups([]); // Ensure groups is an array even if the fetch fails
      }
    };

    fetchGroups();
  }, []);

  const handleAddToGroup = async () => {
    if (!selectedGroup) {
      console.error('No group selected');
      return;
    }

    if (!subscriptionDetails?.id) {
      console.error('No subscription ID available');
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      console.error('No access token found');
      return;
    }

    console.log('Attempting to add subscription to group:', { selectedGroup, subscriptionDetails });

    try {
      const response = await fetch(`http://127.0.0.1:8000/subscriptions/${subscriptionDetails.id}/add-to-group`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          group_id: parseInt(selectedGroup) // Ensure group_id is sent as a number
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(`HTTP error! status: ${response.status}${errorData ? ` - ${JSON.stringify(errorData)}` : ''}`);
      }

      const result = await response.json();
      console.log('Successfully added subscription to group:', result);
      // Show success message
      alert('Successfully added subscription to group!');
    } catch (error) {
      console.error('Error adding subscription to group:', error);
      // Show error message
      alert(`Failed to add subscription to group: ${error.message}`);
    }
  };

  if (loading || !subscriptionDetails) {
    return <div>Loading...</div>;
  }

  const generatedInfo = location.state?.generatedInfo || {};
  const { cancellation_link, alternatives } = generatedInfo;

  // Format and sort the previous dates in descending order
  const previousDates = location.state?.previousDates || [];
  const sortedDates = previousDates
    .map(date => {
      const d = new Date(date);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    })
    .sort((a, b) => new Date(b) - new Date(a)); // Sort in descending order

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          {subscriptionDetails.Description}
        </h1>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label htmlFor="group-select" className="block text-sm font-medium mb-1">Add to Group:</label>
            <select
              id="group-select"
              value={selectedGroup}
              onChange={(e) => setSelectedGroup(e.target.value)}
              className="bg-gray-800 text-white p-2 rounded-lg"
            >
              <option value="">Select a group</option>
              {groups.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.group_name}
                </option>
              ))}
            </select>
            <button
              onClick={handleAddToGroup}
              className="bg-purple-600 text-white font-semibold py-2 px-4 rounded-lg transition duration-300 hover:bg-purple-700"
            >
              Add
            </button>
          </div>
          {cancellation_link && (
            <a href={cancellation_link} target="_blank" rel="noopener noreferrer" className="bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-3 px-8 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50">
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
                {sortedDates.length > 0 ? (
                  sortedDates.map((date, index) => (
                    <tr key={index} className="border-b border-gray-700">
                      <td className="py-2 px-4 text-sm text-gray-300">{date}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="py-2 px-4 text-sm text-gray-300">No previous payment dates available.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300">
          <h2 className="text-2xl font-semibold mb-4">Upcoming Payment</h2>
          <p className="text-gray-300">
            Next Payment: <span className="text-purple-400">{new Date(subscriptionDetails.Estimated_Next).toISOString().split('T')[0]}</span>
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