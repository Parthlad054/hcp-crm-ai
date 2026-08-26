/**
 * useInactivityLogout
 *
 * Automatically logs the user out after a period of inactivity.
 *
 * Behaviours:
 *  - 15 minutes of no user activity  → immediate logout
 *  - Page hidden for 5 minutes        → logout when timer fires
 *    (covers screen-off, device-lock, tab switch)
 *  - Tab / window closed              → handled by sessionStorage (no code needed here)
 *
 * Mount this hook once at the App level so it runs for the entire session.
 */
import { useEffect, useRef } from "react";
import { useDispatch, useSelector } from "react-redux";
import { logout, selectIsAuthenticated } from "../redux/slices/authSlice";

const IDLE_TIMEOUT_MS    = 15 * 60 * 1000; // 15 minutes
const HIDDEN_TIMEOUT_MS  =  5 * 60 * 1000; //  5 minutes

// Events that count as "user is active"
const ACTIVITY_EVENTS = [
  "mousemove",
  "mousedown",
  "keydown",
  "touchstart",
  "scroll",
  "click",
  "pointerdown",
];

export default function useInactivityLogout() {
  const dispatch       = useDispatch();
  const isAuthenticated = useSelector(selectIsAuthenticated);

  // Refs so interval/timeout IDs survive re-renders without causing them
  const idleTimer   = useRef(null);
  const hiddenTimer = useRef(null);

  useEffect(() => {
    // Only activate when the user is logged in
    if (!isAuthenticated) return;

    // ── Helpers ───────────────────────────────────────────────────────────────

    const doLogout = () => {
      clearTimeout(idleTimer.current);
      clearTimeout(hiddenTimer.current);
      dispatch(logout());
    };

    const resetIdleTimer = () => {
      clearTimeout(idleTimer.current);
      idleTimer.current = setTimeout(doLogout, IDLE_TIMEOUT_MS);
    };

    // ── Visibility change (screen off / device lock / tab switch) ────────────
    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden") {
        // Start the hidden-page countdown
        hiddenTimer.current = setTimeout(doLogout, HIDDEN_TIMEOUT_MS);
      } else {
        // User came back — cancel the hidden countdown, reset idle timer
        clearTimeout(hiddenTimer.current);
        resetIdleTimer();
      }
    };

    // ── Wire up ───────────────────────────────────────────────────────────────

    // Start idle timer immediately
    resetIdleTimer();

    // Reset idle timer on any activity
    ACTIVITY_EVENTS.forEach((evt) =>
      window.addEventListener(evt, resetIdleTimer, { passive: true })
    );

    // Watch for tab visibility changes
    document.addEventListener("visibilitychange", handleVisibilityChange);

    // ── Cleanup on unmount or when auth state changes ────────────────────────
    return () => {
      clearTimeout(idleTimer.current);
      clearTimeout(hiddenTimer.current);
      ACTIVITY_EVENTS.forEach((evt) =>
        window.removeEventListener(evt, resetIdleTimer)
      );
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [isAuthenticated, dispatch]);
}
