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

// ── Forgot Password Panel (3-step OTP flow) ───────────────────────────────────
function ForgotPasswordPanel({ onBack }) {
  // step: 'email' → 'otp' → 'password'
  const [step, setStep]         = useState("email");
  const [email, setEmail]       = useState("");
  const [otp, setOtp]           = useState(["", "", "", "", "", ""]);
  const [newPwd, setNewPwd]     = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [showPwd, setShowPwd]   = useState(false);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");
  const [success, setSuccess]   = useState("");
  const otpRefs = Array.from({ length: 6 }, () => React.useRef(null));

  // ── Step 1: send OTP ────────────────────────────────────────────────────────
  const handleSendOtp = async (e) => {
    e.preventDefault();
    setError("");
    if (!email.trim()) { setError("Please enter your email address."); return; }
    setLoading(true);
    try {
      await apiClient.post("/auth/forgot-password", { email });
      setStep("otp");
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // ── OTP input helpers ───────────────────────────────────────────────────────
  const handleOtpChange = (idx, val) => {
    // Accept only single digit
    const digit = val.replace(/\D/g, "").slice(-1);
    const next = [...otp];
    next[idx] = digit;
    setOtp(next);
    setError("");
    if (digit && idx < 5) otpRefs[idx + 1].current?.focus();
  };

  const handleOtpKeyDown = (idx, e) => {
    if (e.key === "Backspace") {
      if (otp[idx]) {
        const next = [...otp]; next[idx] = ""; setOtp(next);
      } else if (idx > 0) {
        otpRefs[idx - 1].current?.focus();
      }
    } else if (e.key === "ArrowLeft" && idx > 0) {
      otpRefs[idx - 1].current?.focus();
    } else if (e.key === "ArrowRight" && idx < 5) {
      otpRefs[idx + 1].current?.focus();
    }
  };

  const handleOtpPaste = (e) => {
    e.preventDefault();
    const text = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (!text) return;
    const next = [...otp];
    text.split("").forEach((d, i) => { next[i] = d; });
    setOtp(next);
    const focusIdx = Math.min(text.length, 5);
    otpRefs[focusIdx].current?.focus();
  };

  // ── Step 2: verify OTP (move to password step) ─────────────────────────────
  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    setError("");
    const code = otp.join("");
    if (code.length < 6) { setError("Please enter all 6 digits."); return; }
    // We don't call an endpoint here — verification happens together with the
    // password reset in step 3, to avoid two round-trips.
    setStep("password");
  };

  // ── Step 3: reset password ──────────────────────────────────────────────────
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError("");
    if (newPwd.length < 8)       { setError("Password must be at least 8 characters."); return; }
    if (!/[A-Z]/.test(newPwd))   { setError("Password must contain at least one uppercase letter."); return; }
    if (!/\d/.test(newPwd))      { setError("Password must contain at least one digit."); return; }
    if (newPwd !== confirmPwd)   { setError("Passwords do not match."); return; }
    setLoading(true);
    try {
      await apiClient.post("/auth/reset-password", {
        email,
        otp: otp.join(""),
        new_password: newPwd,
      });
      setSuccess("Password reset successfully! Redirecting to login…");
      setTimeout(onBack, 2200);
    } catch (err) {
      const msg = err.response?.data?.detail || "Invalid or expired OTP.";
      setError(msg);
      // If OTP was wrong/expired, send user back to OTP step
      if (err.response?.status === 400) {
        setTimeout(() => { setStep("otp"); setOtp(["","","","","",""]); setError(msg); }, 100);
      }
    } finally {
      setLoading(false);
    }
  };

  // ── Step metadata ───────────────────────────────────────────────────────────
  const STEPS = {
    email:    { title: "Forgot password?",    sub: "Enter your registered email and we'll send a 6-digit reset code." },
    otp:      { title: "Enter your code",     sub: `We sent a 6-digit code to ${email}. Check your inbox (and spam).` },
    password: { title: "Set new password",    sub: "Almost done — choose a strong new password." },
  };

  return (
    <div>
      <button
        className="auth-link"
        style={{ marginBottom: 20, display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}
        onClick={step === "password" ? () => setStep("otp") : onBack}
      >
        ← {step === "password" ? "Back" : "Back to login"}
      </button>

      {/* Step indicators */}
      <div className="otp-steps">
        {["email", "otp", "password"].map((s, i) => (
          <div key={s} className={`otp-step-dot ${step === s ? "active" : (["email","otp","password"].indexOf(step) > i ? "done" : "")}`} />
        ))}
      </div>

      <h2 className="auth-title">{STEPS[step].title}</h2>
      <p className="auth-subtitle">{STEPS[step].sub}</p>

      {error   && <div className="auth-alert error"   role="alert">{error}</div>}
      {success && <div className="auth-alert success" role="alert">{success}</div>}

      {/* ── Step 1: Email ─────────────────────────────────────────────────── */}
      {step === "email" && (
        <form className="auth-form" onSubmit={handleSendOtp} noValidate>
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
                autoFocus
              />
            </div>
          </div>
          <button id="forgot-submit-btn" className="auth-btn" type="submit" disabled={loading}>
            {loading && <span className="auth-spinner" />}
            {loading ? "Sending…" : "Send code"}
          </button>
        </form>
      )}

      {/* ── Step 2: OTP boxes ─────────────────────────────────────────────── */}
      {step === "otp" && (
        <form className="auth-form" onSubmit={handleVerifyOtp} noValidate>
          <div className="otp-box-group" onPaste={handleOtpPaste}>
            {otp.map((digit, idx) => (
              <input
                key={idx}
                ref={otpRefs[idx]}
                id={`otp-digit-${idx}`}
                type="text"
                inputMode="numeric"
                maxLength={1}
                className={`otp-box${digit ? " filled" : ""}${error ? " error" : ""}`}
                value={digit}
                onChange={(e) => handleOtpChange(idx, e.target.value)}
                onKeyDown={(e) => handleOtpKeyDown(idx, e)}
                autoFocus={idx === 0}
                autoComplete="one-time-code"
              />
            ))}
          </div>
          <button id="otp-verify-btn" className="auth-btn" type="submit" disabled={otp.join("").length < 6}>
            Verify code →
          </button>
          <p style={{ textAlign: "center", fontSize: 13, color: "var(--text-mid)", marginTop: 4 }}>
            Didn't receive it?{" "}
            <button type="button" className="auth-link" onClick={() => { setStep("email"); setOtp(["","","","","",""]); setError(""); }}>
              Resend
            </button>
          </p>
        </form>
      )}

      {/* ── Step 3: New password ──────────────────────────────────────────── */}
      {step === "password" && (
        <form className="auth-form" onSubmit={handleResetPassword} noValidate>
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
                autoFocus
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
            {loading ? "Saving…" : "Reset password"}
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
