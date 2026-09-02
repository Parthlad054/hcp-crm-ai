import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import apiClient from "../../api/client";

// ── Async thunks ──────────────────────────────────────────────────────────────

export const loginUser = createAsyncThunk(
  "auth/login",
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const { data } = await apiClient.post("/auth/login", { email, password });
      return data?.data || data;
    } catch (err) {
      return rejectWithValue(
        err.response?.data?.message || err.response?.data?.detail || "Login failed. Please try again."
      );
    }
  }
);

export const registerUser = createAsyncThunk(
  "auth/register",
  async (payload, { rejectWithValue }) => {
    try {
      const { data } = await apiClient.post("/auth/register", payload);
      return data?.data || data;
    } catch (err) {
      return rejectWithValue(
        err.response?.data?.message || err.response?.data?.detail || "Registration failed. Please try again."
      );
    }
  }
);

export const refreshAccessToken = createAsyncThunk(
  "auth/refresh",
  async (_, { getState, rejectWithValue }) => {
    try {
      const refreshToken = getState().auth.refreshToken;
      const { data } = await apiClient.post("/auth/refresh", {
        refresh_token: refreshToken,
      });
      return data?.data || data;
    } catch (err) {
      return rejectWithValue("Session expired. Please log in again.");
    }
  }
);

export const fetchCurrentUser = createAsyncThunk(
  "auth/me",
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await apiClient.get("/auth/me");
      return data?.data || data;
    } catch (err) {
      return rejectWithValue(
        err.response?.data?.message || err.response?.data?.detail || "Failed to fetch user"
      );
    }
  }
);

// ── Slice ─────────────────────────────────────────────────────────────────────

// ACCESS_TOKEN_EXPIRE_MINUTES must stay in sync with backend config.py
const ACCESS_TOKEN_EXPIRE_MS = 15 * 60 * 1000;

const initialState = {
  user: null,
  accessToken: null,
  refreshToken: null,
  tokenExpiresAt: null, // Unix ms — when the current access token expires
  status: "idle", // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.tokenExpiresAt = null;
      state.status = "idle";
      state.error = null;
    },
    clearError(state) {
      state.error = null;
    },
    setTokens(state, action) {
      state.accessToken = action.payload.access_token;
      state.refreshToken = action.payload.refresh_token;
      state.tokenExpiresAt = Date.now() + ACCESS_TOKEN_EXPIRE_MS;
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginUser.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.tokenExpiresAt = Date.now() + ACCESS_TOKEN_EXPIRE_MS;
        if (action.payload.user) {
          state.user = action.payload.user;
        }
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      });

    // Register
    builder
      .addCase(registerUser.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.tokenExpiresAt = Date.now() + ACCESS_TOKEN_EXPIRE_MS;
        if (action.payload.user) {
          state.user = action.payload.user;
        }
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      });

    // Refresh
    builder
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        state.accessToken = action.payload.access_token;
        state.refreshToken = action.payload.refresh_token;
        state.tokenExpiresAt = Date.now() + ACCESS_TOKEN_EXPIRE_MS;
        if (action.payload.user) {
          state.user = action.payload.user;
        }
      })
      .addCase(refreshAccessToken.rejected, (state) => {
        // Token refresh failed — force logout
        state.user = null;
        state.accessToken = null;
        state.refreshToken = null;
        state.tokenExpiresAt = null;
        state.status = "idle";
      });

    // Fetch current user
    builder
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload;
      })
      .addCase(fetchCurrentUser.rejected, (state) => {
        state.user = null;
      });
  },
});

export const { logout, clearError, setTokens } = authSlice.actions;

// ── Selectors ─────────────────────────────────────────────────────────────────
export const selectIsAuthenticated = (state) =>
  !!state.auth.accessToken &&
  !!state.auth.tokenExpiresAt &&
  Date.now() < state.auth.tokenExpiresAt;
export const selectCurrentUser = (state) => state.auth.user;
export const selectAuthStatus = (state) => state.auth.status;
export const selectAuthError = (state) => state.auth.error;
export const selectTokenExpiry = (state) => state.auth.tokenExpiresAt;

export default authSlice.reducer;
