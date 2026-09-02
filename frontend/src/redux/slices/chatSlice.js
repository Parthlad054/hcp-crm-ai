import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import apiClient from "../../api/client";
import { mergeFormData } from "./formSlice";

export const sendChatMessage = createAsyncThunk(
  "chat/sendMessage",
  async ({ message, sessionId, currentFormState }, { dispatch, rejectWithValue }) => {
    try {
      const { data: resBody } = await apiClient.post("/chat/", {
        message,
        session_id: sessionId,
        current_form_state: currentFormState ?? null,
      });
      const data = resBody?.data || resBody;

      if (data.form_data != null) {
        dispatch(mergeFormData(data.form_data));
      }

      return data;
    } catch (err) {
      return rejectWithValue(
        err.response?.data?.message || err.response?.data?.detail || err.message || "Failed to send message"
      );
    }
  }
);

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    sessionId: null,
    status: "idle",
    error: null,
  },
  reducers: {
    resetSession: (state) => {
      state.sessionId = null;
      state.status = "idle";
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.status = "idle";
        state.sessionId = action.payload.session_id;
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload || action.error.message;
      });
  },
});

export const { resetSession } = chatSlice.actions;
export default chatSlice.reducer;
