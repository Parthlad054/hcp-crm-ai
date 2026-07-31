import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  selectIsAuthenticated,
  selectCurrentUser,
  logout,
  fetchCurrentUser,
} from "./redux/slices/authSlice";
import LogScreen from "./components/LogScreen/LogScreen";
import LoginPage from "./components/Auth/LoginPage";
import SignUpPage from "./components/Auth/SignUpPage";
import "./App.css";

function App() {
  const dispatch = useDispatch();
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const currentUser = useSelector(selectCurrentUser);

  // Simple client-side page state: 'login' | 'signup'
  const [authPage, setAuthPage] = useState("login");

  // On mount, fetch user profile if we already have a token (persisted session)
  useEffect(() => {
    if (isAuthenticated && !currentUser) {
      dispatch(fetchCurrentUser());
    }
  }, [isAuthenticated, currentUser, dispatch]);

  const handleLogout = () => {
    dispatch(logout());
  };

  // ── Not authenticated: show auth pages ──────────────────────────────────────
  if (!isAuthenticated) {
    if (authPage === "signup") {
      return (
        <SignUpPage
          onNavigateLogin={() => setAuthPage("login")}
        />
      );
    }
    return (
      <LoginPage
        onNavigateSignUp={() => setAuthPage("signup")}
      />
    );
  }

  // ── Authenticated: show the main app ────────────────────────────────────────
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-brand">
          <span className="header-logo">⚕️</span>
          <div>
            <h1 className="header-title">HCP CRM AI</h1>
            <span className="header-sub">Life Sciences Field CRM</span>
          </div>
        </div>
        <div className="header-right">
          <div className="rep-badge">
            <span className="rep-avatar">
              {currentUser?.name ? currentUser.name.charAt(0).toUpperCase() : "U"}
            </span>
            <span className="rep-name">
              {currentUser?.name || "User"}
            </span>
          </div>
          <button
            id="logout-btn"
            onClick={handleLogout}
            style={{
              marginLeft: 12,
              padding: "6px 14px",
              background: "transparent",
              border: "1px solid #e2e8f0",
              borderRadius: 8,
              cursor: "pointer",
              fontSize: 13,
              color: "#475569",
              fontFamily: "inherit",
              fontWeight: 500,
              transition: "background 0.15s",
            }}
            onMouseEnter={(e) => (e.target.style.background = "#f1f5f9")}
            onMouseLeave={(e) => (e.target.style.background = "transparent")}
          >
            Sign out
          </button>
        </div>
      </header>

      <main className="app-main">
        <LogScreen />
      </main>
    </div>
  );
}

export default App;
