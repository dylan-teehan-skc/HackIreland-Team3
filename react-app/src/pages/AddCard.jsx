import React from 'react';
import { useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import CardForm from '../components/CardForm';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

const AddCard = () => {
  const navigate = useNavigate();

  const handleSuccess = () => {
    alert('Card added successfully!');
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Add Payment Card
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Your card information is securely processed by Stripe
          </p>
        </div>

        <div className="mt-8">
          <Elements stripe={stripePromise}>
            <CardForm onSuccess={handleSuccess} />
          </Elements>
        </div>
      </div>
    </div>
  );
};

export default AddCard;
