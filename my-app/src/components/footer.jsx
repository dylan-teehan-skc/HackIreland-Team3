import React from "react";
import { Link } from "react-router-dom";
import footerImage from "../images/sampleicon.png";

const Footer = () => {
  return (
    <footer className="w-full bg-gray-900 text-gray-300 py-6 flex flex-col md:flex-row justify-between items-center">
        <div className="flex items-center">
          <div className="ml-[10%] w-64 h-16 flex items-center justify-center">
            <img src={footerImage} alt="Logo" />
          </div>
        </div>
        <div className="flex flex-wrap space-x-6 mt-2 sm:mt-0">
          <Link
            to="/"
            className="text-m text-gray-300 hover:text-white hover:underline"
          >
            Home
          </Link>
          <Link
            to="/dashboard"
            className="text-m text-gray-300 hover:text-white hover:underline"
          >
            Dashboard
          </Link>
        </div>
        <div className="mr-[5%] text-center md:text-right mt-4 md:mt-0">
          &copy; 2025 SubClub. All rights reserved.
        </div>
    </footer>
  );
};

export default Footer;