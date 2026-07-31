import React from "react";
import { useSelector } from "react-redux";
import { selectIsAuthenticated } from "../../redux/slices/authSlice";

/**
 * ProtectedRoute — wraps any component that requires authentication.
 * If the user is not logged in, it renders null (App.jsx handles the redirect).
 */
export default function ProtectedRoute({ children }) {
  const isAuthenticated = useSelector(selectIsAuthenticated);

  if (!isAuthenticated) {
    // App.jsx will render LoginPage instead; this component simply returns null
    return null;
  }

  return children;
}
