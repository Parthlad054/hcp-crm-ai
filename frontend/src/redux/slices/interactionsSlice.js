import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import apiClient from "../../api/client";

// ── Async thunks ───────────────────────────────────────────────────────────

export const createInteraction = createAsyncThunk(
  "interactions/create",
  async (payload, { rejectWithValue }) => {
    try {
      const { data } = await apiClient.post("/interactions/", payload);
      return data;
    } catch (err) {
      return rejectWithValue(
        err.response?.data?.detail || err.message || "Failed to log interaction"
      );
    }
  }
);

// ── Slice ──────────────────────────────────────────────────────────────────

const interactionsSlice = createSlice({
  name: "interactions",
  initialState: {
    status: "idle",   // idle | loading | succeeded | failed
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(createInteraction.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(createInteraction.fulfilled, (state) => {
        state.status = "succeeded";
      })
      .addCase(createInteraction.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload || action.error.message;
      });
  },
});

export default interactionsSlice.reducer;
