import React, { useState } from 'react';
import { CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const CARD_ELEMENT_OPTIONS = {
  style: {
    base: {
      color: '#32325d',
      fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
      fontSmoothing: 'antialiased',
      fontSize: '16px',
      '::placeholder': {
        color: '#aab7c4'
      }
    },
    invalid: {
      color: '#fa755a',
      iconColor: '#fa755a'
    }
  }
};

const CardForm = ({ onSuccess }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState(null);
  const [cardHolderName, setCardHolderName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!stripe || !elements) return;

    setLoading(true);
    setError(null);

    try {
      const { paymentMethod, error } = await stripe.createPaymentMethod({
        type: 'card',
        card: elements.getElement(CardElement),
        billing_details: {
          name: cardHolderName,
        },
      });

      if (error) {
        setError(error.message);
        return;
      }

      const response = await fetch('http://localhost:8000/real-cards/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          payment_method_id: paymentMethod.id,
          card_holder_name: cardHolderName,
        }),
      });

      if (!response.ok) {
        const text = await response.text();
        let errorMessage = 'Failed to add card';
        try {
          const data = JSON.parse(text);
          errorMessage = data.detail || errorMessage;
        } catch (e) {
          console.error('Failed to parse error response:', text);
        }
        throw new Error(errorMessage);
      }
      
      const data = await response.json();

      onSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto space-y-6">
      <div className="space-y-2">
        <label htmlFor="cardHolderName" className="block text-sm font-medium text-gray-700">
          Card Holder Name
        </label>
        <input
          type="text"
          id="cardHolderName"
          value={cardHolderName}
          onChange={(e) => setCardHolderName(e.target.value)}
          required
          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Card Details
        </label>
        <div className="p-3 border border-gray-300 rounded-md shadow-sm">
          <CardElement options={CARD_ELEMENT_OPTIONS} />
        </div>
      </div>

      {error && (
        <div className="text-red-600 text-sm">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={!stripe || loading}
        className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
          loading ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        {loading ? 'Adding Card...' : 'Add Card'}
      </button>
    </form>
  );
};

export default CardForm;
