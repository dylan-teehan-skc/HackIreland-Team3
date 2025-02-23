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
    <div className="min-h-screen bg-gray-900 text-white flex flex-col justify-center items-center p-6">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-gray-900 to-gray-900 opacity-75 -z-10"></div>

      {/* Main Content */}
      <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          Add Payment Card
        </h1>
        <p className="text-lg text-gray-300 mb-8 text-center">
          Your card information is securely processed by Stripe.
        </p>

        {/* Stripe Elements Wrapper */}
        <div className="mt-6">
          <Elements stripe={stripePromise}>
            <CardForm onSuccess={handleSuccess} />
          </Elements>
        </div>
      </div>

      {/* Animated Blobs */}
      <div className="absolute w-64 h-64 bg-purple-600 rounded-full opacity-20 blur-3xl animate-blob animation-delay-2000 -top-32 -left-32"></div>
      <div className="absolute w-64 h-64 bg-pink-600 rounded-full opacity-20 blur-3xl animate-blob animation-delay-4000 -bottom-32 -right-32"></div>
    </div>
  );
};

export default AddCard;