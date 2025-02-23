import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const SplitSubscription = () => {
  const [splitSubscriptions, setSplitSubscriptions] = useState([]);
  const [showCreateGroupModal, setShowCreateGroupModal] = useState(false);
  const [groupName, setGroupName] = useState("");
  const [members, setMembers] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSubscription, setSelectedSubscription] = useState(null);
  const [splitRatios, setSplitRatios] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSplitSubscriptions = async () => {
      try {
        const response = await fetch("/api/split-subscriptions", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        });
        const data = await response.json();
        setSplitSubscriptions(data);
      } catch (err) {
        console.error("Failed to fetch split subscriptions:", err);
      }
    };

    fetchSplitSubscriptions();
  }, []);

  const handleCreateGroup = async () => {
    try {
      const response = await fetch("/api/groups", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ name: groupName, members }),
      });

      const data = await response.json();
      if (response.ok) {
        setShowCreateGroupModal(false);
        setGroupName("");
        setMembers([]);
        alert("Group created successfully!");
      } else {
        alert(data.detail || "Failed to create group.");
      }
    } catch (err) {
      console.error("Error creating group:", err);
    }
  };

  const handleAddSubscription = async () => {
    try {
      const response = await fetch("/api/subscriptions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          groupId: selectedSubscription.groupId,
          subscriptionId: selectedSubscription.id,
          splitRatios,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        alert("Subscription added successfully!");
        setSelectedSubscription(null);
        setSplitRatios({});
      } else {
        alert(data.detail || "Failed to add subscription.");
      }
    } catch (err) {
      console.error("Error adding subscription:", err);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-4xl font-bold mb-8">Split Subscriptions</h1>
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Your Split Subscriptions</h2>
        <table className="w-full bg-gray-800 rounded-lg overflow-hidden">
          <thead>
            <tr className="bg-gray-700">
              <th className="px-6 py-3 text-left">Group Name</th>
              <th className="px-6 py-3 text-left">Subscription</th>
              <th className="px-6 py-3 text-left">Split Ratios</th>
            </tr>
          </thead>
          <tbody>
            {splitSubscriptions.map((subscription, index) => (
              <tr key={index} className="border-b border-gray-700">
                <td className="px-6 py-4">{subscription.groupName}</td>
                <td className="px-6 py-4">{subscription.subscriptionName}</td>
                <td className="px-6 py-4">
                  {Object.entries(subscription.splitRatios).map(([user, ratio]) => (
                    <div key={user}>
                      {user}: {ratio}%
                    </div>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        onClick={() => setShowCreateGroupModal(true)}
        className="bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-2 px-4 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50"
      >
        Create Group
      </button>

      {showCreateGroupModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
          <div className="bg-gray-800 p-8 rounded-lg w-full max-w-md">
            <h2 className="text-2xl font-bold mb-6">Create Group</h2>
            <input
              type="text"
              placeholder="Group Name"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-purple-600"
            />
            <input
              type="text"
              placeholder="Search for users"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-purple-600"
            />
            <div className="mb-4">
              {members.map((member, index) => (
                <div key={index} className="flex justify-between items-center bg-gray-700 p-2 rounded-lg mb-2">
                  <span>{member}</span>
                  <button
                    onClick={() => setMembers(members.filter((m) => m !== member))}
                    className="text-red-500 hover:text-red-600"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
            <button
              onClick={handleCreateGroup}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-2 px-4 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50"
            >
              Create Group
            </button>
            <button
              onClick={() => setShowCreateGroupModal(false)}
              className="w-full bg-gray-700 text-white font-semibold py-2 px-4 rounded-lg mt-4 transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-gray-500/50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {selectedSubscription && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
          <div className="bg-gray-800 p-8 rounded-lg w-full max-w-md">
            <h2 className="text-2xl font-bold mb-6">Add Shared Subscription</h2>
            <div className="mb-4">
              {members.map((member) => (
                <div key={member} className="flex justify-between items-center bg-gray-700 p-2 rounded-lg mb-2">
                  <span>{member}</span>
                  <input
                    type="number"
                    placeholder="Percentage"
                    value={splitRatios[member] || ""}
                    onChange={(e) =>
                      setSplitRatios({ ...splitRatios, [member]: e.target.value })
                    }
                    className="w-20 px-2 py-1 bg-gray-600 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                  />
                </div>
              ))}
            </div>
            <button
              onClick={handleAddSubscription}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-2 px-4 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50"
            >
              Confirm
            </button>
            <button
              onClick={handleAddSubscription}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-2 px-4 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50"
            >
              Return
            </button>
            <button
              onClick={() => setSelectedSubscription(null)}
              className="w-full bg-gray-700 text-white font-semibold py-2 px-4 rounded-lg mt-4 transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-gray-500/50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SplitSubscription;