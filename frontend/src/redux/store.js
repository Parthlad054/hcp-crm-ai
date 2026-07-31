import { configureStore } from "@reduxjs/toolkit";
import interactionsReducer from "./slices/interactionsSlice";
import chatReducer from "./slices/chatSlice";
import formReducer from "./slices/formSlice";
import authReducer from "./slices/authSlice";

const loadState = () => {
  try {
    const serializedState = localStorage.getItem("hcp_crm_state");
    if (serializedState === null) return undefined;
    return JSON.parse(serializedState);
  } catch (err) {
    return undefined;
  }
};

const saveState = (state) => {
  try {
    const stateToSave = {
      chat: state.chat,
      form: state.form,
      // Persist only tokens — not loading/error states
      auth: {
        accessToken: state.auth.accessToken,
        refreshToken: state.auth.refreshToken,
        user: state.auth.user,
        status: "idle",
        error: null,
      },
    };
    const serializedState = JSON.stringify(stateToSave);
    localStorage.setItem("hcp_crm_state", serializedState);
  } catch (err) {
    console.error("Could not save state", err);
  }
};

export const store = configureStore({
  reducer: {
    interactions: interactionsReducer,
    chat: chatReducer,
    form: formReducer,
    auth: authReducer,
  },
  preloadedState: loadState(),
});

store.subscribe(() => {
  saveState(store.getState());
});
