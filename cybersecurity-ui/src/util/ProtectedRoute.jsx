// src/components/ProtectedRoute.js
import React from "react";
import { useSelector } from "react-redux";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ element }) => {
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated); // Get the authentication state from Redux

  // Return JSX here
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return element;
};

export default ProtectedRoute;
