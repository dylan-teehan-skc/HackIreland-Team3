import { AreaChart, BarChart, Area, Bar } from "recharts";
import { useNavigate } from "react-router-dom";

const DashboardPage = () => {
    const navigate = useNavigate();

    // Sample data - replace with your backend data
    const subscriptions = [
        {
            id: "1",
            name: "Netflix",
            amount: 12.99,
            nextPayment: "2024-03-05",
            daysRemaining: 13,
            type: "Entertainment"
        },
        {
            id: "2",
            name: "Spotify",
            amount: 9.99,
            nextPayment: "2024-03-10",
            daysRemaining: 8,
            type: "Music"
        },
    ];

    // Sample chart data
    const paymentHistory = [
        { date: "2024-01", amount: 120 },
        { date: "2024-02", amount: 135 },
        { date: "2024-03", amount: 150 },
    ];

    // Calculate projected expenses
    const projectedExpenses = subscriptions.reduce(
        (sum, sub) => sum + sub.amount,
        0
    );

    const handleRowClick = (subscriptionId) => {
        navigate(`/subscriptions/${subscriptionId}`);
    };

    return (
        <div className="min-h-screen p-8 space-y-6">
            <h1 className="text-3xl font-bold">Subscription Dashboard</h1>

            {/* Payment Timeline Table */}
            <div className="border p-4 rounded-lg">
                <h2 className="text-xl font-semibold">Active Subscriptions</h2>
                <p className="text-gray-600">Upcoming payments and details</p>
                <table className="w-full mt-4">
                    <thead>
                        <tr>
                            <th className="text-left">Payment Date</th>
                            <th className="text-left">Subscription</th>
                            <th className="text-left">Amount</th>
                            <th className="text-left">Days Remaining</th>
                            <th className="text-left">Type</th>
                        </tr>
                    </thead>
                    <tbody>
                        {subscriptions.map((sub) => (
                            <tr 
                                key={sub.id}
                                onClick={() => handleRowClick(sub.id)}
                                className="cursor-pointer hover:bg-gray-50"
                            >
                                <td>{new Date(sub.nextPayment).toLocaleDateString()}</td>
                                <td className="font-medium">{sub.name}</td>
                                <td>${sub.amount}</td>
                                <td>{sub.daysRemaining} days</td>
                                <td>{sub.type}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Historical Spending */}
                <div className="border p-4 rounded-lg">
                    <h2 className="text-xl font-semibold">Spending Over Time</h2>
                    <p className="text-gray-600">Monthly subscription costs</p>
                    <AreaChart
                        width={500}
                        height={300}
                        data={paymentHistory}
                        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                    >
                        <defs>
                            <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                                <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <Area
                            type="monotone"
                            dataKey="amount"
                            stroke="#8884d8"
                            fillOpacity={1}
                            fill="url(#colorAmount)"
                        />
                    </AreaChart>
                </div>

                {/* Projected Expenses */}
                <div className="border p-4 rounded-lg">
                    <h2 className="text-xl font-semibold">Next Month's Projection</h2>
                    <p className="text-gray-600">Expected subscription costs</p>
                    <div className="text-4xl font-bold mb-4">
                        ${projectedExpenses}
                    </div>
                    <BarChart
                        width={500}
                        height={300}
                        data={subscriptions}
                        margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                        <Bar dataKey="amount" fill="#82ca9d" />
                    </BarChart>
                </div>
            </div>

            {/* Active Subscriptions List */}
            <div className="border p-4 rounded-lg">
                <h2 className="text-xl font-semibold">All Active Subscriptions</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {subscriptions.map((sub) => (
                        <div 
                            key={sub.id}
                            onClick={() => handleRowClick(sub.id)}
                            className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                        >
                            <h3 className="font-semibold">{sub.name}</h3>
                            <p className="text-sm text-gray-500">${sub.amount}/month</p>
                            <p className="text-sm text-gray-500">
                                Next payment: {new Date(sub.nextPayment).toLocaleDateString()}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default DashboardPage;