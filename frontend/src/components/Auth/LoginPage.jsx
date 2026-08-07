import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { loginUser, selectAuthStatus, selectAuthError, clearError } from "../../redux/slices/authSlice";
import apiClient from "../../api/client";
import "./Auth.css";

// ── Icons (inline SVG as components) ─────────────────────────────────────────
const MailIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
  </svg>
);
const LockIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
);
const EyeIcon = ({ show }) => show ? (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
    <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
    <line x1="1" y1="1" x2="23" y2="23"/>
  </svg>
) : (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
  </svg>
);

// ── Forgot Password Panel ─────────────────────────────────────────────────────
function ForgotPasswordPanel({ onBack }) {
  const [step, setStep] = useState("request"); // 'request' | 'success' | 'reset'
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showPwd, setShowPwd] = useState(false);

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setError("");
    if (!email) { setError("Please enter your email address."); return; }
    setLoading(true);
    try {
      await apiClient.post("/auth/forgot-password", { email });
      setStep("success");
      setSuccess("A password reset link has been sent to your email.");
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError("");
    if (!token) { setError("Please enter the reset token from your email."); return; }
    if (newPwd.length < 8) { setError("Password must be at least 8 characters."); return; }
    if (newPwd !== confirmPwd) { setError("Passwords do not match."); return; }
    setLoading(true);
    try {
      await apiClient.post("/auth/reset-password", { token, new_password: newPwd });
      setSuccess("Password reset successfully! You can now log in.");
      setTimeout(onBack, 2500);
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid or expired token.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button className="auth-link" style={{ marginBottom: 20, display: "flex", alignItems: "center", gap: 6, fontSize: 13 }} onClick={onBack}>
        ← Back to login
      </button>

      <h2 className="auth-title">
        {step === "request" ? "Forgot password?" : step === "success" ? "Check your email" : "Reset password"}
      </h2>
      <p className="auth-subtitle">
        {step === "request"
          ? "Enter your registered email and we'll send a reset link."
          : step === "success"
          ? "We sent a reset link to your email. Enter the token below."
          : "Enter the token from your email and set a new password."}
      </p>

      {error && <div className="auth-alert error" role="alert">{error}</div>}
      {success && <div className="auth-alert success" role="alert">{success}</div>}

      {step === "request" && (
        <form className="auth-form" onSubmit={handleRequestReset} noValidate>
          <div className="auth-field">
            <label htmlFor="forgot-email">Email address</label>
            <div className="auth-input-wrap">
              <span className="auth-input-icon"><MailIcon /></span>
              <input
                id="forgot-email"
                type="email"
                className="auth-input"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
              />
            </div>
          </div>
          <button id="forgot-submit-btn" className="auth-btn" type="submit" disabled={loading}>
            {loading && <span className="auth-spinner" />}
            {loading ? "Sending…" : "Send reset link"}
          </button>
        </form>
      )}

      {step === "success" && (
        <form className="auth-form" onSubmit={handleResetPassword} noValidate>
          <div className="auth-field">
            <label htmlFor="reset-token">Reset token (from email)</label>
            <div className="auth-input-wrap">
              <span className="auth-input-icon"><LockIcon /></span>
              <input
                id="reset-token"
                type="text"
                className="auth-input"
                placeholder="Paste the token from your email"
                value={token}
                onChange={(e) => setToken(e.target.value)}
              />
            </div>
          </div>
          <div className="auth-field">
            <label htmlFor="new-password">New password</label>
            <div className="auth-input-wrap">
              <span className="auth-input-icon"><LockIcon /></span>
              <input
                id="new-password"
                type={showPwd ? "text" : "password"}
                className="auth-input"
                placeholder="Min 8 chars, 1 uppercase, 1 digit"
                value={newPwd}
                onChange={(e) => setNewPwd(e.target.value)}
                autoComplete="new-password"
              />
              <button type="button" className="auth-input-toggle" onClick={() => setShowPwd(!showPwd)} aria-label="Toggle password">
                <EyeIcon show={showPwd} />
              </button>
            </div>
          </div>
          <div className="auth-field">
            <label htmlFor="confirm-new-password">Confirm new password</label>
            <div className="auth-input-wrap">
              <span className="auth-input-icon"><LockIcon /></span>
              <input
                id="confirm-new-password"
                type={showPwd ? "text" : "password"}
                className="auth-input"
                placeholder="Repeat your new password"
                value={confirmPwd}
                onChange={(e) => setConfirmPwd(e.target.value)}
                autoComplete="new-password"
              />
            </div>
          </div>
          <button id="reset-submit-btn" className="auth-btn" type="submit" disabled={loading}>
            {loading && <span className="auth-spinner" />}
            {loading ? "Resetting…" : "Reset password"}
          </button>
        </form>
      )}
    </div>
  );
}

// ── Login Page ────────────────────────────────────────────────────────────────
export default function LoginPage({ onNavigateSignUp }) {
  const dispatch = useDispatch();
  const status = useSelector(selectAuthStatus);
  const apiError = useSelector(selectAuthError);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [showForgot, setShowForgot] = useState(false);

  const loading = status === "loading";

  const validate = () => {
    const errs = {};
    if (!email.trim()) errs.email = "Email is required.";
    else if (!/\S+@\S+\.\S+/.test(email)) errs.email = "Enter a valid email.";
    if (!password) errs.password = "Password is required.";
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    dispatch(clearError());
    const errs = validate();
    setFieldErrors(errs);
    if (Object.keys(errs).length) return;
    await dispatch(loginUser({ email, password }));
  };

  if (showForgot) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="auth-brand">
            <span className="auth-brand-icon">⚕️</span>
            <div>
              <div className="auth-brand-name">HCP CRM AI</div>
              <div className="auth-brand-sub">Life Sciences Field CRM</div>
            </div>
          </div>
          <ForgotPasswordPanel onBack={() => setShowForgot(false)} />
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Brand */}
        <div className="auth-brand">
          <span className="auth-brand-icon">⚕️</span>
          <div>
            <div className="auth-brand-name">HCP CRM AI</div>
            <div className="auth-brand-sub">Life Sciences Field CRM</div>
          </div>
        </div>

        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Sign in to your account to continue</p>

        {apiError && (
          <div className="auth-alert error" role="alert">
            {Array.isArray(apiError)
              ? apiError.map((e) => e.msg || JSON.stringify(e)).join(", ")
              : typeof apiError === "string"
              ? apiError
              : "Login failed. Please check your details."}
          </div>
        )}

        <form id="login-form" className="auth-form" onSubmit={handleSubmit} noValidate>
          {/* Email */}
          <div className="auth-field">
            <label htmlFor="login-email">Email address</label>
            <div className="auth-input-wrap">
              <span className="auth-input-icon"><MailIcon /></span>
              <input
                id="login-email"
                type="email"
                className={`auth-input${fieldErrors.email ? " error" : ""}`}
                placeholder="you@example.com"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setFieldErrors((p) => ({ ...p, email: "" })); }}
                autoComplete="email"
                disabled={loading}
              />
            </div>
            {fieldErrors.email && <span className="auth-field-error">{fieldErrors.email}</span>}
          </div>

          {/* Password */}
          <div className="auth-field">
            <label htmlFor="login-password">Password</label>
            <div className="auth-input-wrap">
              <span className="auth-input-icon"><LockIcon /></span>
              <input
                id="login-password"
                type={showPwd ? "text" : "password"}
                className={`auth-input${fieldErrors.password ? " error" : ""}`}
                placeholder="Your password"
                value={password}
                onChange={(e) => { setPassword(e.target.value); setFieldErrors((p) => ({ ...p, password: "" })); }}
                autoComplete="current-password"
                disabled={loading}
              />
              <button type="button" className="auth-input-toggle" onClick={() => setShowPwd(!showPwd)} aria-label="Toggle password visibility">
                <EyeIcon show={showPwd} />
              </button>
            </div>
            {fieldErrors.password && <span className="auth-field-error">{fieldErrors.password}</span>}
          </div>

          {/* Forgot link */}
          <div className="auth-forgot-row">
            <button type="button" className="auth-link" onClick={() => setShowForgot(true)}>
              Forgot password?
            </button>
          </div>

          <button id="login-submit-btn" className="auth-btn" type="submit" disabled={loading}>
            {loading && <span className="auth-spinner" />}
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="auth-footer">
          Don't have an account?{" "}
          <button className="auth-link" onClick={onNavigateSignUp}>
            Create one
          </button>
        </p>
      </div>
    </div>
  );
}
