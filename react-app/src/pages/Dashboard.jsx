import React, { useEffect, useState, useContext } from "react";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Link, useNavigate } from "react-router-dom";
import { FileContext } from "../context/FileContext"; // Import the FileContext

// Register the necessary components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [totalSpent, setTotalSpent] = useState(0);
  const { fileId, setFileId } = useContext(FileContext); // Use the FileContext
  const navigate = useNavigate();

  useEffect(() => {
    if (!fileId) return; // Do nothing if fileId is not set

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
  }, [fileId]); // Fetch subscriptions whenever fileId changes

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

        // Navigate with the generated info
        navigate(`/subscription/${fileId}/${encodeURIComponent(description)}/${amount}`, { state: { generatedInfo: data } });
    } catch (error) {
        console.error("Error generating subscription info:", error);
    }
  };

  const data = {
    labels: subscriptions.map(sub => sub.Date),
    datasets: [
      {
        label: 'Spending',
        data: subscriptions.map(sub => sub.Amount),
        backgroundColor: 'rgba(99, 102, 241, 0.6)',
        borderColor: 'rgba(99, 102, 241, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Monthly Subscription Spending',
        color: '#fff',
        font: {
          size: 18,
        },
      },
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

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="flex justify-between items-center mb-8">
        {/* Title */}
        <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent leading-tight">
          Your Subscriptions
        </h1>

        {/* File Upload */}
        <input type="file" onChange={handleFileUpload} className="text-gray-300" />
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
                {subscriptions.map((sub) => (
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
          <h2 className="text-2xl font-semibold text-gray-300 mb-6">Monthly Spending</h2>
          <div style={{ height: '500px' }}> {/* Fixed height for the chart */}
            <Bar data={data} options={options} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;