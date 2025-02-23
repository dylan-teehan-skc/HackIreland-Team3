import React, { createContext, useState } from 'react';

export const SubscriptionContext = createContext();

export const SubscriptionProvider = ({ children }) => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [totalSpent, setTotalSpent] = useState(0);

  return (
    <SubscriptionContext.Provider value={{ subscriptions, setSubscriptions, totalSpent, setTotalSpent }}>
      {children}
    </SubscriptionContext.Provider>
  );
}; 