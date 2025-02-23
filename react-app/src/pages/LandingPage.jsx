import React from "react";
import { Link } from "react-router-dom";
import Placeholder from "../images/Stripe-1.jpeg"
import DashboardImage from "../images/dashboardv1.png"
import InsightsImage from "../images/insightsv1.png"
import SplitsImage from "../images/splitv1.png"

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col justify-center items-center p-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-gray-900 to-gray-900 opacity-75 -z-10"></div>

      <div className="min-h-screen flex flex-col justify-center items-center p-6 overflow-hidden max-w-2xl relative z-10">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent animate-gradient">
          Take Control of Your Subscriptions
        </h1>

        <p className="text-lg md:text-xl text-gray-300 mb-12 leading-relaxed">
          SubHub - The unified system to manage, split and save on all your subscriptions
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/dashboard"
            className="relative bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50"
          >
            <span className="relative z-10">Go to Dashboard</span>
            <span className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg opacity-0 hover:opacity-100 transition-opacity duration-300"></span>
          </Link>
          <Link
            to="/groups"
            className="relative bg-transparent border-2 border-purple-600 hover:border-purple-700 text-purple-600 hover:text-purple-700 font-semibold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50"
          >
            <span className="relative z-10">Your Groups</span>
            <span className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg opacity-0 hover:opacity-10 transition-opacity duration-300"></span>
          </Link>
        </div>
      </div>

      <div className="w-full max-w-6xl mt-20 space-y-16">
        <div className="relative p-8 bg-gray-800 rounded-lg shadow-lg">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 opacity-10 rounded-lg -z-10"></div>
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="flex-1">
              <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
                Track All Your Subscriptions
              </h2>
              <p className="text-lg text-gray-300">
                Keep track of all your subscriptions in one place. Integrate your account directly with your bank card to track your subscriptions and view them
                on the dashboard.
              </p>
            </div>
            <div className="flex-1">
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-1 rounded-lg">
                <div className="bg-gray-900 p-6 rounded-lg">
                  <img
                    src={DashboardImage}
                    alt="Subscription Tracking"
                    className="rounded-lg"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="relative p-8 bg-gray-800 rounded-lg shadow-lg">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 opacity-10 rounded-lg -z-10"></div>
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="flex-1 order-2 md:order-1">
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-1 rounded-lg">
                <div className="bg-gray-900 p-6 rounded-lg">
                  <img
                    src={SplitsImage}
                    alt="Split Expenses"
                    className="rounded-lg"
                  />
                </div>
              </div>
            </div>
            <div className="flex-1 order-1 md:order-2">
              <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
                Split Expenses with Ease
              </h2>
              <p className="text-lg text-gray-300">
                Share subscription costs with friends or family. Create a group to hold a virtual card with to set split ratios for your payments.
                Never worry about splitting bills again with our automatic billing split.
              </p>
            </div>
          </div>
        </div>

        <div className="relative p-8 bg-gray-800 rounded-lg shadow-lg">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 opacity-10 rounded-lg -z-10"></div>
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="flex-1">
              <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
                Insights & Analytics
              </h2>
              <p className="text-lg text-gray-300">
                Get detailed insights into your spending habits. Understand where
                your money is going and optimise your subscriptions. Analyse your projected expenses for upcoming Months
                and cancel your subscription easily from our site.
              </p>
            </div>
            <div className="flex-1">
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-1 rounded-lg">
                <div className="bg-gray-900 p-6 rounded-lg">
                  <img
                    src={InsightsImage}
                    alt="Insights & Analytics"
                    className="rounded-lg"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      

        <div className="relative p-8 bg-gray-800 rounded-lg shadow-lg">
          <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 opacity-10 rounded-lg -z-10"></div>
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="flex-1 order-2 md:order-1">
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-1 rounded-lg">
                <div className="bg-gray-900 p-6 rounded-lg">
                  <img
                    src={Placeholder}
                    alt="Split Expenses"
                    className="rounded-lg"
                  />
                </div>
              </div>
            </div>
            <div className="flex-1 order-1 md:order-2">
              <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
                Our Stripe API Integration
              </h2>
              <p className="text-lg text-gray-300">
                Our Stripe API Integration lets you seamlessly add a virtual card, split payments, and create set ratios for subscription splits. It's convenient, quick, and secure.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute w-64 h-64 bg-purple-600 rounded-full opacity-20 blur-3xl animate-blob animation-delay-2000 -top-32 -left-32"></div>
      <div className="absolute w-64 h-64 bg-pink-600 rounded-full opacity-20 blur-3xl animate-blob animation-delay-4000 -bottom-32 -right-32"></div>
    </div>
  );
};

export default LandingPage;