import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import apiClient from "../../api/client";

// ── Async thunks ───────────────────────────────────────────────────────────

export const searchHCPs = createAsyncThunk(
  "hcps/search",
  async (query = "") => {
    const { data } = await apiClient.get("/hcps/", { params: { q: query } });
    return data;
  }
);

// ── Slice ──────────────────────────────────────────────────────────────────

const hcpSlice = createSlice({
  name: "hcps",
  initialState: {
    list: [],
    selectedHCP: null,
    status: "idle",
    error: null,
  },
  reducers: {
    selectHCP(state, action) {
      state.selectedHCP = action.payload;
    },
    clearHCPSelection(state) {
      state.selectedHCP = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(searchHCPs.pending, (state) => { state.status = "loading"; })
      .addCase(searchHCPs.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.list = action.payload;
      })
      .addCase(searchHCPs.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      });
  },
});

export const { selectHCP, clearHCPSelection } = hcpSlice.actions;
export default hcpSlice.reducer;
