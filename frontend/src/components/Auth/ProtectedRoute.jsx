import React from "react";
import { useSelector } from "react-redux";
import { selectIsAuthenticated } from "../../redux/slices/authSlice";

/**
 * ProtectedRoute — wraps components that require authentication.
 * If not authenticated, renders the fallback component (e.g. LoginPage / SignUpPage).
 */
export default function ProtectedRoute({ children, fallback }) {
  const isAuthenticated = useSelector(selectIsAuthenticated);

  if (!isAuthenticated) {
    return fallback || null;
  }

  return children;
}

