import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import apiClient from "../../api/client";

// ── Async thunks ───────────────────────────────────────────────────────────

export const sendChatMessage = createAsyncThunk(
  "chat/sendMessage",
  async ({ message, sessionId }) => {
    const { data } = await apiClient.post("/chat/", {
      message,
      session_id: sessionId,
    });
    return data;
  }
);

// ── Slice ──────────────────────────────────────────────────────────────────

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    messages: [],       // [{ role: "user"|"agent", content: string }]
    sessionId: null,
    status: "idle",     // idle | loading | failed
    error: null,
  },
  reducers: {
    addUserMessage(state, action) {
      state.messages.push({ role: "user", content: action.payload });
    },
    clearChat(state) {
      state.messages = [];
      state.sessionId = null;
      state.status = "idle";
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => { state.status = "loading"; })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.status = "idle";
        state.sessionId = action.payload.session_id;
        state.messages.push({ role: "agent", content: action.payload.reply });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      });
  },
});

export const { addUserMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
