import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { registerUser, selectAuthStatus, selectAuthError, clearError } from "../../redux/slices/authSlice";
import "./Auth.css";

// ── Inline SVG icons ──────────────────────────────────────────────────────────
const UserIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
  </svg>
);
const PhoneIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.07 11.5 19.79 19.79 0 0 1 1 2.88a2 2 0 0 1 2-2.18H6a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81A2 2 0 0 1 8.25 7l-1.2 1.2a16 16 0 0 0 6.79 6.79L15 13.8a2 2 0 0 1 2.44-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
  </svg>
);
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

// ── Password strength helper ───────────────────────────────────────────────────
function getPasswordStrength(pwd) {
  if (!pwd) return { score: 0, label: "", cls: "" };
  let score = 0;
  if (pwd.length >= 8) score++;
  if (/[A-Z]/.test(pwd)) score++;
  if (/\d/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  if (score <= 1) return { score, label: "Weak", cls: "weak" };
  if (score === 2) return { score, label: "Fair", cls: "medium" };
  if (score === 3) return { score, label: "Good", cls: "medium" };
  return { score, label: "Strong", cls: "strong" };
}

// ── SignUp Page ───────────────────────────────────────────────────────────────
export default function SignUpPage({ onNavigateLogin }) {
  const dispatch = useDispatch();
  const status = useSelector(selectAuthStatus);
  const apiError = useSelector(selectAuthError);

  const [form, setForm] = useState({
    name: "",
    contact_number: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [showPwd, setShowPwd] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});

  const loading = status === "loading";
  const strength = getPasswordStrength(form.password);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setFieldErrors((prev) => ({ ...prev, [field]: "" }));
    dispatch(clearError());
  };

  const validate = () => {
    const errs = {};
    if (!form.name.trim() || form.name.trim().length < 2)
      errs.name = "Name must be at least 2 characters.";
    if (!form.contact_number.trim())
      errs.contact_number = "Contact number is required.";
    else if (!/^\+?\d{7,15}$/.test(form.contact_number.replace(/[\s\-\(\)]/g, "")))
      errs.contact_number = "Enter a valid phone number (7–15 digits).";
    if (!form.email.trim())
      errs.email = "Email is required.";
    else if (!/\S+@\S+\.\S+/.test(form.email))
      errs.email = "Enter a valid email address.";
    if (!form.password)
      errs.password = "Password is required.";
    else if (form.password.length < 8)
      errs.password = "Password must be at least 8 characters.";
    else if (!/[A-Z]/.test(form.password))
      errs.password = "Password needs at least one uppercase letter.";
    else if (!/\d/.test(form.password))
      errs.password = "Password needs at least one digit.";
    if (form.confirm_password !== form.password)
      errs.confirm_password = "Passwords do not match.";
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    dispatch(clearError());
    const errs = validate();
    setFieldErrors(errs);
    if (Object.keys(errs).length) return;
    await dispatch(registerUser(form));
  };

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

        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Join HCP CRM AI — it only takes a minute</p>

        {/* API error banner */}
        {apiError && (
          <div className="auth-alert error" role="alert">
            {Array.isArray(apiError)
              ? apiError.map((e) => e.msg || JSON.stringify(e)).join(", ")
              : typeof apiError === "string"
              ? apiError
              : "Registration failed. Please check your details."}
          </div>
        )}

        <form id="signup-form" className="auth-form" onSubmit={handleSubmit} noValidate>
          {/* Full name */}
          <div className="auth-field">
            <label htmlFor="signup-name">Full name</label>
            <div className="auth-input-wrap">
              <span className="auth-input-icon"><UserIcon /></span>
              <input
                id="signup-name"
                type="text"
                className={`auth-input${fieldErrors.name ? " error" : ""}`}
                placeholder="Dr. Jane Smith"
                value={form.name}
                onChange={handleChange("name")}
                autoComplete="name"
                disabled={loading}
              />
            </div>
            {fieldErrors.name && <span className="auth-field-error">{fieldErrors.name}</span>}
          </div>

          {/* Contact number */}
          <div className="auth-field">
            <label htmlFor="signup-phone">Contact number</label>
            <div className="auth-input-wrap">
              <span className="auth-input-icon"><PhoneIcon /></span>
              <input
                id="signup-phone"
                type="tel"
                className={`auth-input${fieldErrors.contact_number ? " error" : ""}`}
                placeholder="+91 98765 43210"
                value={form.contact_number}
                onChange={handleChange("contact_number")}
                autoComplete="tel"
                disabled={loading}
              />
            </div>
            {fieldErrors.contact_number && <span className="auth-field-error">{fieldErrors.contact_number}</span>}
          </div>

          {/* Email */}
          <div className="auth-field">
            <label htmlFor="signup-email">Email address</label>
            <div className="auth-input-wrap">
              <span className="auth-input-icon"><MailIcon /></span>
              <input
                id="signup-email"
                type="email"
                className={`auth-input${fieldErrors.email ? " error" : ""}`}
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange("email")}
                autoComplete="email"
                disabled={loading}
              />
            </div>
            {fieldErrors.email && <span className="auth-field-error">{fieldErrors.email}</span>}
          </div>

          {/* Password */}
          <div className="auth-field">
            <label htmlFor="signup-password">Password</label>
            <div className="auth-input-wrap">
              <span className="auth-input-icon"><LockIcon /></span>
              <input
                id="signup-password"
                type={showPwd ? "text" : "password"}
                className={`auth-input${fieldErrors.password ? " error" : ""}`}
                placeholder="Min 8 chars, 1 uppercase, 1 digit"
                value={form.password}
                onChange={handleChange("password")}
                autoComplete="new-password"
                disabled={loading}
              />
              <button type="button" className="auth-input-toggle" onClick={() => setShowPwd(!showPwd)} aria-label="Toggle password">
                <EyeIcon show={showPwd} />
              </button>
            </div>
            {/* Strength bar */}
            {form.password && (
              <>
                <div className="pwd-strength-bar" aria-label={`Password strength: ${strength.label}`}>
                  {[1, 2, 3, 4].map((i) => (
                    <span key={i} className={i <= strength.score ? strength.cls : ""} />
                  ))}
                </div>
                <div className={`pwd-strength-label ${strength.cls}`}>{strength.label}</div>
              </>
            )}
            {fieldErrors.password && <span className="auth-field-error">{fieldErrors.password}</span>}
          </div>

          {/* Confirm Password */}
          <div className="auth-field">
            <label htmlFor="signup-confirm">Confirm password</label>
            <div className="auth-input-wrap">
              <span className="auth-input-icon"><LockIcon /></span>
              <input
                id="signup-confirm"
                type={showConfirm ? "text" : "password"}
                className={`auth-input${fieldErrors.confirm_password ? " error" : ""}`}
                placeholder="Repeat your password"
                value={form.confirm_password}
                onChange={handleChange("confirm_password")}
                autoComplete="new-password"
                disabled={loading}
              />
              <button type="button" className="auth-input-toggle" onClick={() => setShowConfirm(!showConfirm)} aria-label="Toggle confirm password">
                <EyeIcon show={showConfirm} />
              </button>
            </div>
            {fieldErrors.confirm_password && <span className="auth-field-error">{fieldErrors.confirm_password}</span>}
          </div>

          <button id="signup-submit-btn" className="auth-btn" type="submit" disabled={loading}>
            {loading && <span className="auth-spinner" />}
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{" "}
          <button className="auth-link" onClick={onNavigateLogin}>
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
}
