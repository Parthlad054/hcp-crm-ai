import { configureStore } from "@reduxjs/toolkit";
import interactionsReducer from "./slices/interactionsSlice";
import chatReducer from "./slices/chatSlice";
import formReducer from "./slices/formSlice";
import authReducer from "./slices/authSlice";

// ── Auth state — sessionStorage ───────────────────────────────────────────────
// sessionStorage is automatically cleared by the browser when the tab/window
// is closed, so "logout on tab close" is handled natively with no extra code.
const AUTH_KEY = "hcp_crm_auth";

const loadAuthState = () => {
  try {
    const raw = sessionStorage.getItem(AUTH_KEY);
    if (!raw) return undefined;
    const auth = JSON.parse(raw);
    // If the access token has already expired, discard the stored session
    // so the user is redirected to login instead of seeing an error flash.
    if (auth.tokenExpiresAt && Date.now() >= auth.tokenExpiresAt) {
      sessionStorage.removeItem(AUTH_KEY);
      return undefined;
    }
    return { auth: { ...auth, status: "idle", error: null } };
  } catch {
    return undefined;
  }
};

const saveAuthState = (auth) => {
  try {
    sessionStorage.setItem(
      AUTH_KEY,
      JSON.stringify({
        accessToken: auth.accessToken,
        refreshToken: auth.refreshToken,
        tokenExpiresAt: auth.tokenExpiresAt,
        user: auth.user,
      })
    );
  } catch (err) {
    console.error("Could not save auth state", err);
  }
};

// ── Non-auth state — localStorage ─────────────────────────────────────────────
// Chat and form state persist across page refreshes but not auth.
const UI_KEY = "hcp_crm_ui";

const loadUiState = () => {
  try {
    const raw = localStorage.getItem(UI_KEY);
    return raw ? JSON.parse(raw) : undefined;
  } catch {
    return undefined;
  }
};

const saveUiState = (state) => {
  try {
    localStorage.setItem(UI_KEY, JSON.stringify({ chat: state.chat, form: state.form }));
  } catch (err) {
    console.error("Could not save UI state", err);
  }
};

// ── Store ──────────────────────────────────────────────────────────────────────
const preloaded = {
  ...(loadAuthState() || {}),
  ...(loadUiState() || {}),
};

export const store = configureStore({
  reducer: {
    interactions: interactionsReducer,
    chat: chatReducer,
    form: formReducer,
    auth: authReducer,
  },
  preloadedState: preloaded,
});

store.subscribe(() => {
  const state = store.getState();
  saveAuthState(state.auth);
  saveUiState(state);
});
