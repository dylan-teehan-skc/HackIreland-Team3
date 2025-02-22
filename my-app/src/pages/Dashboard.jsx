// app/dashboard/dashboard.jsx
import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    CardDescription,
  } from "@/components/ui/card";
  import { Input } from "@/components/ui/input";
  import { Button } from "@/components/ui/button";
  import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "@/components/ui/table";
  import { AreaChart } from "recharts";
  import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui/dropdown-menu";
  
  export default function Dashboard() {
    const subscriptions = [
      // Add your subscription data here
      { name: "Netflix", cost: 12.99, billingDate: "5th", daysRemaining: "13d 3hr", type: "Manage/split" },
      // ... duplicate entries as needed
    ];
  
    return (
      <div className="min-h-screen bg-gray-50 p-8 space-y-8">
        {/* Header Section */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="space-y-1">
            <h1 className="text-2xl font-bold tracking-tight">SUBHUB</h1>
            <p className="text-sm text-muted-foreground">Hope</p>
          </div>
          <div className="flex flex-1 justify-end items-center gap-2 w-full md:w-auto">
            <Input 
              placeholder="Search subscription" 
              className="max-w-xs focus-visible:ring-1" 
            />
            <Button variant="outline" className="shrink-0">
              Filter
            </Button>
          </div>
        </header>
  
        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column (2/3 width on large screens) */}
          <div className="lg:col-span-2 space-y-6">
            {/* Subscription Table Card */}
            <Card className="shadow-sm">
              <CardHeader className="px-6 pt-6 pb-4">
                <CardTitle className="text-lg">Subscriptions</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader className="bg-gray-50/50">
                    <TableRow>
                      <TableHead className="w-[200px]">Name</TableHead>
                      <TableHead className="text-right">Cost (C)</TableHead>
                      <TableHead>Billing Date</TableHead>
                      <TableHead>Days Remaining</TableHead>
                      <TableHead className="text-right">Type</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {subscriptions.map((sub, index) => (
                      <TableRow key={index} className="hover:bg-gray-50/30">
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-3">
                            <div className="h-8 w-8 bg-muted rounded-md" />
                            <span>{sub.name}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">${sub.cost}</TableCell>
                        <TableCell>{sub.billingDate}</TableCell>
                        <TableCell>{sub.daysRemaining}</TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger className="text-primary hover:underline">
                              {sub.type}
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem>Manage</DropdownMenuItem>
                              <DropdownMenuItem>Split</DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
  
            {/* Total Expenditure Card */}
            <Card className="shadow-sm">
              <CardHeader className="py-4 px-6">
                <CardTitle className="text-lg">Total Monthly Expenditure</CardTitle>
              </CardHeader>
              <CardContent className="py-2 px-6">
                <div className="text-3xl font-bold text-primary">$217.84</div>
              </CardContent>
            </Card>
          </div>
  
          {/* Right Column (1/3 width on large screens) */}
          <div className="space-y-6">
            {/* Calendar Card */}
            <Card className="shadow-sm">
              <CardHeader className="py-4 px-6">
                <CardTitle className="text-lg">Calendar of Payments</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-muted/20 rounded-lg border border-dashed flex items-center justify-center text-muted-foreground">
                  Calendar Preview
                </div>
              </CardContent>
            </Card>
  
            {/* Chart Card */}
            <Card className="shadow-sm">
              <CardHeader className="py-4 px-6">
                <div className="space-y-1">
                  <CardTitle className="text-lg">Subscription Trends</CardTitle>
                  <CardDescription className="text-sm">
                    January-June 2024
                  </CardDescription>
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <div className="h-full bg-muted/20 rounded-lg border border-dashed flex items-center justify-center text-muted-foreground">
                    Chart Preview
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }