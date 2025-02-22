import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import SplitSubscription from "./SplitSubscription";

const SubscriptionDetails = () => {
  const { id } = useParams();
  const [subscription, setSubscription] = useState(null);

  // Mock data for subscription details (replace with API call)
  useEffect(() => {
    const fetchSubscription = async () => {
      // Simulate an API call
      setTimeout(() => {
        setSubscription({
          id: id,
          name: "Netflix",
          cost: 15.99,
          dueDate: "2023-11-15",
          paymentMethod: "Credit Card",
          paymentHistory: [
            { date: "2023-10-15", amount: 15.99 },
            { date: "2023-09-15", amount: 15.99 },
          ],
        });
      }, 500);
    };

    fetchSubscription();
  }, [id]);

  if (!subscription) {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">{subscription.name}</h1>
      <div className="space-y-4">
        {/* Monthly Cost */}
        <div>
          <h2 className="text-xl font-semibold">Monthly Cost</h2>
          <p>${subscription.cost}</p>
        </div>

        {/* Billing Data */}
        <div>
          <h2 className="text-xl font-semibold">Billing Data</h2>
          <p>Due Date: {subscription.dueDate}</p>
          <p>Payment Method: {subscription.paymentMethod}</p>
        </div>

        {/* Payment History */}
        <div>
          <h2 className="text-xl font-semibold">Payment History</h2>
          <ul>
            {subscription.paymentHistory.map((payment, index) => (
              <li key={index}>
                {payment.date}: ${payment.amount}
              </li>
            ))}
          </ul>
        </div>

        {/* Split Subscription Component */}
        <SplitSubscription subscriptionId={id} />
      </div>
    </div>
  );
};

export default SubscriptionDetails;