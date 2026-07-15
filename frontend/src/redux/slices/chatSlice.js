import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import apiClient from "../../api/client";
import { mergeFormData } from "./formSlice";

export const sendChatMessage = createAsyncThunk(
  "chat/sendMessage",
  async ({ message, sessionId, currentFormState }, { dispatch }) => {
    const { data } = await apiClient.post("/chat/", {
      message,
      session_id: sessionId,
      current_form_state: currentFormState ?? null,
    });

    if (data.form_data != null) {
      dispatch(mergeFormData(data.form_data));
    }

    return data;
  }
);

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    sessionId: null,
    status: "idle",
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.status = "loading";
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.status = "idle";
        state.sessionId = action.payload.session_id;
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      });
  },
});

export default chatSlice.reducer;
