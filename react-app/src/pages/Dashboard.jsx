import React, { useEffect, useContext, useState } from "react";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Link, useNavigate } from "react-router-dom";
import { FileContext } from "../context/FileContext";
import { SubscriptionContext } from "../context/SubscriptionContext"; // Import the SubscriptionContext

// Register the necessary components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const { subscriptions, setSubscriptions, totalSpent, setTotalSpent } = useContext(SubscriptionContext); // Use the SubscriptionContext
  const { fileId, setFileId } = useContext(FileContext);
  const navigate = useNavigate();

  const [timeRange, setTimeRange] = useState('Monthly'); // State to manage time range selection
  const [selectedMonth, setSelectedMonth] = useState(''); // State to manage selected month

  // Extract unique months from subscriptions
  const availableMonths = [...new Set(subscriptions.map(sub => new Date(sub.Date).toLocaleString('default', { month: 'long', year: 'numeric' })))];

  useEffect(() => {
    if (!fileId) return;

    const fetchSubscriptions = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/subscriptions/subscriptions/sorted/${fileId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setSubscriptions(data);

        const total = data.reduce((sum, sub) => sum + sub.Amount, 0);
        setTotalSpent(total);
      } catch (error) {
        console.error("Error fetching subscriptions:", error);
      }
    };

    fetchSubscriptions();
  }, [fileId, setSubscriptions, setTotalSpent]);

  const handleDelete = async (description, amount, date) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/subscriptions/subscriptions/${fileId}/${encodeURIComponent(description)}/${amount}/${date}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Remove the subscription from the state
      setSubscriptions((prevSubscriptions) =>
        prevSubscriptions.filter((sub) => !(sub.Description === description && sub.Amount === amount && sub.Date === date))
      );

      // Recalculate the total spent
      const newTotal = subscriptions.reduce((sum, sub) => sum + sub.Amount, 0);
      setTotalSpent(newTotal);
    } catch (error) {
      console.error("Error deleting subscription:", error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:8000/files/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setFileId(data.file_id); // Update the file ID, triggering the useEffect to fetch data
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  const fetchPreviousDates = async (description, amount) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/subscriptions/filter/${fileId}?description=${encodeURIComponent(description)}&price=${amount}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const filteredSubscriptions = await response.json();
      return filteredSubscriptions.flatMap(sub => sub.Dates);
    } catch (error) {
      console.error("Error fetching previous dates:", error);
      return [];
    }
  };

  const handleDescriptionClick = async (description, amount, dates) => {
    console.log("Description:", description);
    console.log("Amount:", amount);
    console.log("Dates:", dates);

    const formattedDates = dates ? dates.map(date => new Date(date).toISOString().split('T')[0]) : [];

    const requestBody = { description, price: amount, dates: formattedDates };
    console.log("Request Body:", requestBody);

    try {
      const response = await fetch("http://127.0.0.1:8000/generate-subscription-info", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        console.error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}`);
        const errorText = await response.text();
        console.error("Error response text:", errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("API Response Data:", data);

      // Fetch previous dates
      const previousDates = await fetchPreviousDates(description, amount);

      // Navigate with the generated info and previous dates
      navigate(`/subscription/${fileId}/${encodeURIComponent(description)}/${amount}`, { state: { generatedInfo: data, previousDates } });
    } catch (error) {
      console.error("Error generating subscription info:", error);
    }
  };

  // Function to handle time range change
  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
    if (event.target.value !== 'Monthly') {
      setSelectedMonth(''); // Reset month selection if not monthly
    }
  };

  // Function to handle month change
  const handleMonthChange = (event) => {
    setSelectedMonth(event.target.value);
  };

  // Prepare data for the chart based on the selected time range and month
  const filteredSubscriptions = timeRange === 'Monthly' && selectedMonth
    ? subscriptions.filter(sub => new Date(sub.Date).toLocaleString('default', { month: 'long', year: 'numeric' }) === selectedMonth)
    : subscriptions;

  const chartData = {
    labels: filteredSubscriptions.map(sub => sub.Date),
    datasets: [
      {
        label: 'Spending',
        data: filteredSubscriptions.map(sub => sub.Amount),
        backgroundColor: 'rgba(99, 102, 241, 0.6)',
        borderColor: 'rgba(99, 102, 241, 1)',
        borderWidth: 1,
        descriptions: filteredSubscriptions.map(sub => sub.Description),
      },
    ],
  };

  // Update the chart options based on the time range
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `${timeRange} Subscription Spending`,
        color: '#fff',
        font: {
          size: 18,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const description = context.dataset.descriptions[context.dataIndex];
            const amount = context.raw;
            return `${description}: $${amount.toFixed(2)}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#fff',
        },
      },
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#fff',
        },
      },
    },
  };

  // Calculate upcoming subscriptions
  const upcomingSubscriptions = subscriptions
    .map(sub => {
      const daysAway = Math.ceil((new Date(sub.Estimated_Next) - new Date()) / (1000 * 60 * 60 * 24));
      return { ...sub, daysAway };
    })
    .filter(sub => sub.daysAway >= 0)
    // Filter out duplicates based on Description
    .filter((sub, index, self) => 
      index === self.findIndex((s) => s.Description === sub.Description)
    )
    .sort((a, b) => a.daysAway - b.daysAway);

  // Sort subscriptions by date in descending order
  const sortedSubscriptions = [...subscriptions].sort((a, b) => new Date(b.Date) - new Date(a.Date));

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="flex justify-between items-center mb-8">
        {/* Title */}
        <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent leading-tight">
          Your Subscriptions
        </h1>

        {/* File Upload */}
        <div className="relative">
          <input 
            type="file" 
            onChange={handleFileUpload} 
            className="hidden" 
            id="file-upload" 
          />
          <label 
            htmlFor="file-upload" 
            className="cursor-pointer bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 
            text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-all duration-200 
            flex items-center space-x-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <span>Upload Statement</span>
          </label>
        </div>
      </div>

      {/* Content Container */}
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Table Section */}
        <div className="flex-1 bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-300 mb-6">Subscription Details</h2>
          <div className="overflow-y-auto" style={{ maxHeight: '500px' }}> {/* Fixed height and scrollable */}
            <table className="min-w-full">
              <thead>
                <tr>
                  <th className="py-3 px-6 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Description</th>
                  <th className="py-3 px-6 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Amount</th>
                  <th className="py-3 px-6 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Date</th>
                  <th className="py-3 px-6 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Upcoming Payment</th>
                  <th className="py-3 px-6 text-left text-xs font-semibold text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedSubscriptions.map((sub) => (
                  <tr key={`${sub.Description}-${sub.Amount}-${sub.Date}`} className="border-b border-gray-700 hover:bg-gray-750 transition-colors duration-200">
                    <td className="py-4 px-6 text-sm font-medium text-gray-300">
                      <button onClick={() => handleDescriptionClick(sub.Description, sub.Amount, sub.Dates)}>
                        {sub.Description}
                      </button>
                    </td>
                    <td className="py-4 px-6 text-sm text-gray-300">${sub.Amount.toFixed(2)}</td>
                    <td className="py-4 px-6 text-sm text-gray-300">{sub.Date}</td>
                    <td className="py-4 px-6 text-sm text-gray-300">{sub.Estimated_Next}</td>
                    <td className="py-4 px-6 text-sm text-gray-300">
                      <button
                        onClick={() => handleDelete(sub.Description, sub.Amount, sub.Date)}
                        className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-md transition-colors duration-200"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-6 text-lg text-gray-300">
            Total Spent in Last 12 Months: <strong>${totalSpent.toFixed(2)}</strong>
          </p>
        </div>

        {/* Chart Section */}
        <div className="flex-1 bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-semibold text-gray-300">{timeRange} Spending</h2>
            <div className="flex space-x-4">
              {/* Time Range Dropdown */}
              <select
                value={timeRange}
                onChange={handleTimeRangeChange}
                className="bg-gray-800 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-all duration-200"
              >
                <option value="Monthly">Monthly</option>
                <option value="Yearly">Yearly</option>
              </select>

              {/* Month Selector (only show if Monthly is selected) */}
              {timeRange === 'Monthly' && (
                <select
                  value={selectedMonth}
                  onChange={handleMonthChange}
                  className="bg-gray-800 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-all duration-200"
                >
                  <option value="">Select Month</option>
                  {availableMonths.map(month => (
                    <option key={month} value={month}>{month}</option>
                  ))}
                </select>
              )}
            </div>
          </div>
          <div style={{ height: '500px' }}> {/* Fixed height for the chart */}
            <Bar data={chartData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Upcoming Subscriptions Section */}
      <div className="mt-8 bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-semibold text-gray-300 mb-6">Upcoming Subscriptions</h2>
        <ul>
          {upcomingSubscriptions.map((sub, index) => (
            <li key={index} className="mb-4">
              <p className="text-lg text-purple-400">{sub.Description}</p>
              <p className="text-gray-300">Next Payment: {sub.Estimated_Next} ({sub.daysAway} days away)</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;