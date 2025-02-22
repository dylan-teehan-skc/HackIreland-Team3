import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const SubscriptionDetails = () => {
  const { id } = useParams();
  const [subscription, setSubscription] = useState(null);

  // Fetch subscription details from the backend
  useEffect(() => {
    const fetchSubscription = async () => {
      const response = await fetch(`/api/subscriptions/${id}`);
      const data = await response.json();
      setSubscription(data);
    };

    fetchSubscription();
  }, [id]);

  if (!subscription) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">{subscription.name}</h1>
      <div className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold">Monthly Cost</h2>
          <p>${subscription.cost}</p>
        </div>
        <div>
          <h2 className="text-xl font-semibold">Billing Data</h2>
          <p>Due Date: {subscription.dueDate}</p>
          <p>Payment Method: {subscription.paymentMethod}</p>
        </div>
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
        <div>
          <h2 className="text-xl font-semibold">Split Subscription</h2>
          <p>Options for splitting this subscription with others:</p>
          <SplitSubscription subscriptionId={id} />
        </div>
      </div>
    </div>
  );
};

export default SubscriptionDetails;