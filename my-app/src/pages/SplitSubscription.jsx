import React, { useState } from "react";

const SplitSubscription = ({ subscriptionId }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [splits, setSplits] = useState([]);
  const [splitRatio, setSplitRatio] = useState(0);

  const mockUsers = [
    { id: 1, name: "Alice", email: "alice@example.com" },
    { id: 2, name: "Bob", email: "bob@example.com" },
    { id: 3, name: "Charlie", email: "charlie@example.com" },
  ];

  // Search for users
  const handleSearch = () => {
    const filteredUsers = mockUsers.filter(
      (user) =>
        user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setSearchResults(filteredUsers);
  };

  // Add a split
  const handleAddSplit = (userId) => {
    const user = mockUsers.find((u) => u.id === userId);
    if (user) {
      setSplits([...splits, { ...user, splitRatio }]);
      setSearchQuery("");
      setSearchResults([]);
    }
  };

  return (
    <div className="mt-8">
      <h2 className="text-xl font-semibold mb-4">Split Subscription</h2>
      <div className="space-y-4">
        {/* Search for users */}
        <div className="flex space-x-2">
          <input
            type="text"
            placeholder="Search for users..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-gray-700 text-white p-2 rounded flex-1"
          />
          <button
            onClick={handleSearch}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Search
          </button>
        </div>

        {/* Search results */}
        {searchResults.length > 0 && (
          <div className="space-y-2">
            {searchResults.map((user) => (
              <div
                key={user.id}
                className="flex justify-between items-center bg-gray-800 p-2 rounded"
              >
                <span>
                  {user.name} ({user.email})
                </span>
                <button
                  onClick={() => handleAddSplit(user.id)}
                  className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
                >
                  Add Split
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Splits table */}
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-800">
                <th className="p-2 text-left">User</th>
                <th className="p-2 text-left">Email</th>
                <th className="p-2 text-left">Split Ratio</th>
              </tr>
            </thead>
            <tbody>
              {splits.map((split, index) => (
                <tr key={index} className="border-b border-gray-700">
                  <td className="p-2">{split.name}</td>
                  <td className="p-2">{split.email}</td>
                  <td className="p-2">{split.splitRatio}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SplitSubscription;