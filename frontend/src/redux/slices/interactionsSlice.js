import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import apiClient from "../../api/client";

// ── Async thunks ───────────────────────────────────────────────────────────

export const fetchInteractions = createAsyncThunk(
  "interactions/fetchByHcp",
  async (hcpId) => {
    const { data } = await apiClient.get(`/interactions/${hcpId}`);
    return data;
  }
);

export const createInteraction = createAsyncThunk(
  "interactions/create",
  async (payload) => {
    const { data } = await apiClient.post("/interactions/", payload);
    return data;
  }
);

export const patchInteraction = createAsyncThunk(
  "interactions/patch",
  async ({ id, payload }) => {
    const { data } = await apiClient.patch(`/interactions/${id}`, payload);
    return data;
  }
);

// ── Slice ──────────────────────────────────────────────────────────────────

const interactionsSlice = createSlice({
  name: "interactions",
  initialState: {
    list: [],
    status: "idle",   // idle | loading | succeeded | failed
    error: null,
  },
  reducers: {
    clearInteractions(state) {
      state.list = [];
      state.status = "idle";
    },
  },
  extraReducers: (builder) => {
    builder
      // fetch
      .addCase(fetchInteractions.pending, (state) => { state.status = "loading"; })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.list = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      })
      // create
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.list.unshift(action.payload);
      })
      // patch
      .addCase(patchInteraction.fulfilled, (state, action) => {
        const idx = state.list.findIndex((i) => i.id === action.payload.id);
        if (idx !== -1) state.list[idx] = action.payload;
      });
  },
});

export const { clearInteractions } = interactionsSlice.actions;
export default interactionsSlice.reducer;
