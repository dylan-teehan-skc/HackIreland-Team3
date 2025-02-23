import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Footer from "./components/Footer";
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import SubscriptionDetails from "./pages/SubscriptionDetails";
import SplitSubscription from "./pages/SplitSubscription";
import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import Account from "./pages/Account";
import AddCard from "./pages/AddCard";
import Groups from "./pages/Groups";
import ProtectedRoute from "./components/ProtectedRoute";
import { FileProvider } from "./context/FileContext";
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <FileProvider>
        <div className="app">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route element={<ProtectedRoute />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/account" element={<Account />} />
                <Route path="/add-card" element={<AddCard />} />
                <Route path="/groups" element={<Groups />} />
                <Route path="/subscription/:id" element={<SubscriptionDetails />} />
                <Route path="/split-subscription" element={<SplitSubscription />} />
              </Route>
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<SignUp />} />
              <Route path="/subscription/:fileId/:description/:amount" element={<SubscriptionDetails />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </FileProvider>
    </BrowserRouter>
  );
}

export default App;
