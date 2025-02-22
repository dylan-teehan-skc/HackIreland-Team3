import React, { useState } from "react";
import { Input } from "./components/ui/input";
import { Button } from "./components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "./components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "./components/ui/table";

const SplitSubscription = ({ subscriptionId }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [splits, setSplits] = useState([]);
  const [splitRatio, setSplitRatio] = useState(0);

  // Search for users
  const handleSearch = async () => {
    const response = await fetch(`http://localhost:5000/api/users/search?query=${searchQuery}`);
    const data = await response.json();
    setSearchResults(data);
  };
  
  const handleAddSplit = async (userId) => {
    const response = await fetch(`http://localhost:5000/api/subscriptions/${subscriptionId}/splits`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId, splitRatio }),
    });
    const data = await response.json();
    if (data.id) {
      fetchSplits(); // Refresh the splits list
    }
  };
  
  const fetchSplits = async () => {
    const response = await fetch(`http://localhost:5000/api/subscriptions/${subscriptionId}/splits`);
    const data = await response.json();
    setSplits(data);
  };

  // Load splits on mount
  React.useEffect(() => {
    fetchSplits();
  }, [subscriptionId]);

  return (
    <Card className="bg-gray-800 text-white">
      <CardHeader>
        <CardTitle>Split Subscription</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Search for users */}
          <div className="flex space-x-2">
            <Input
              type="text"
              placeholder="Search for users..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-gray-700 text-white"
            />
            <Button onClick={handleSearch}>Search</Button>
          </div>

          {/* Search results */}
          {searchResults.length > 0 && (
            <div className="space-y-2">
              {searchResults.map((user) => (
                <div key={user.id} className="flex justify-between items-center">
                  <span>
                    {user.name} ({user.email})
                  </span>
                  <Button onClick={() => handleAddSplit(user.id)}>Add Split</Button>
                </div>
              ))}
            </div>
          )}

          {/* Splits table */}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Split Ratio</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {splits.map((split) => (
                <TableRow key={split.id}>
                  <TableCell>{split.name}</TableCell>
                  <TableCell>{split.email}</TableCell>
                  <TableCell>{split.splitRatio}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default SplitSubscription;