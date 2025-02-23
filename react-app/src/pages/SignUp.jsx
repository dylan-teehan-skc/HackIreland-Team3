import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const SignUp = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch("http://localhost:8000/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, email, password }),
      });

      if (!response.ok) {
        throw new Error("Sign up failed. Please try again.");
      }

      const data = await response.json();
      localStorage.setItem("access_token", data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "An error occurred. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col justify-center items-center p-6">
      <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-3xl font-bold mb-6 text-center bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          Sign Up
        </h1>
        {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-gray-300 mb-2">
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
              required
            />
          </div>
          <div>
            <label htmlFor="email" className="block text-gray-300 mb-2">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
              required
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-gray-300 mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-2 px-4 rounded-lg transition duration-300 transform hover:scale-105 hover:shadow-lg hover:shadow-purple-500/50"
          >
            Sign Up
          </button>
        </form>
        <p className="text-gray-300 mt-6 text-center">
          Already have an account?{" "}
          <Link to="/login" className="text-purple-400 hover:text-purple-500">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
};

export default SignUp;