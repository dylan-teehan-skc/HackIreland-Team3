// app/dashboard/page.tsx
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    CardDescription,
  } from "@/components/ui/card";
  import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "@/components/ui/table";
  import { Button } from "@/components/ui/button";
  import { AreaChart, BarChart } from "recharts";
  import { useRouter } from "next/navigation";
  
  const DashboardPage = () => {
    const router = useRouter();
    
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
  
    const handleRowClick = (subscriptionId: string) => {
      router.push(`/subscriptions/${subscriptionId}`);
    };
  
    return (
      <div className="min-h-screen p-8 space-y-6">
        <h1 className="text-3xl font-bold">Subscription Dashboard</h1>
  
        {/* Payment Timeline Table */}
        <Card>
          <CardHeader>
            <CardTitle>Active Subscriptions</CardTitle>
            <CardDescription>Upcoming payments and details</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Payment Date</TableHead>
                  <TableHead>Subscription</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Days Remaining</TableHead>
                  <TableHead>Type</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {subscriptions.map((sub) => (
                  <TableRow 
                    key={sub.id}
                    onClick={() => handleRowClick(sub.id)}
                    className="cursor-pointer hover:bg-gray-50"
                  >
                    <TableCell>{new Date(sub.nextPayment).toLocaleDateString()}</TableCell>
                    <TableCell className="font-medium">{sub.name}</TableCell>
                    <TableCell>${sub.amount}</TableCell>
                    <TableCell>{sub.daysRemaining} days</TableCell>
                    <TableCell>
                      <Button variant="outline" className="capitalize">
                        {sub.type}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
  
        {/* Charts Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Historical Spending */}
          <Card>
            <CardHeader>
              <CardTitle>Spending Over Time</CardTitle>
              <CardDescription>Monthly subscription costs</CardDescription>
            </CardHeader>
            <CardContent>
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
            </CardContent>
          </Card>
  
          {/* Projected Expenses */}
          <Card>
            <CardHeader>
              <CardTitle>Next Month's Projection</CardTitle>
              <CardDescription>Expected subscription costs</CardDescription>
            </CardHeader>
            <CardContent>
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
            </CardContent>
          </Card>
        </div>
  
        {/* Active Subscriptions List */}
        <Card>
          <CardHeader>
            <CardTitle>All Active Subscriptions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
          </CardContent>
        </Card>
      </div>
    );
  };
  
  export default DashboardPage;