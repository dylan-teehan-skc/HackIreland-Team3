import React from "react";

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Navbar */}
      <nav className="p-6 border-b border-gray-800">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">SubClub</h1>
          <div className="flex space-x-4">
            <button className="text-gray-400 hover:text-white">Login</button>
            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Sign Up
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-6 py-20 text-center">
        <h1 className="text-5xl font-bold mb-6">
          Take Control of Your Subscriptions
        </h1>
        <p className="text-xl text-gray-400 mb-8">
          SubClub helps you manage, track, and split recurring expenses with ease.
          Never miss a payment again!
        </p>
        <button className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700">
          Get Started
        </button>

        {/* Hero Graphic */}
        <div className="mt-16">
          <img
            src="https://illustrations.popsy.co/amber/online-payments.svg"
            alt="Subscription Management"
            className="mx-auto w-full max-w-2xl"
          />
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-gray-800 py-20">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12">Why SubClub?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="text-center">
              <img
                src="https://illustrations.popsy.co/amber/digital-nomad.svg"
                alt="Easy Overview"
                className="mx-auto w-32 h-32 mb-4"
              />
              <h3 className="text-xl font-semibold mb-2">Easy Overview</h3>
              <p className="text-gray-400">
                See all your subscriptions in one place with clear due dates and
                costs.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="text-center">
              <img
                src="https://illustrations.popsy.co/amber/reminder.svg"
                alt="Timely Reminders"
                className="mx-auto w-32 h-32 mb-4"
              />
              <h3 className="text-xl font-semibold mb-2">Timely Reminders</h3>
              <p className="text-gray-400">
                Get alerts before payments are due so you never miss a renewal.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="text-center">
              <img
                src="https://illustrations.popsy.co/amber/split-bill.svg"
                alt="Flexible Sharing"
                className="mx-auto w-32 h-32 mb-4"
              />
              <h3 className="text-xl font-semibold mb-2">Flexible Sharing</h3>
              <p className="text-gray-400">
                Split subscription costs with friends, family, or colleagues
                effortlessly.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="p-6 border-t border-gray-800">
        <div className="container mx-auto text-center text-gray-400">
          <p>© 2023 SubClub. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;