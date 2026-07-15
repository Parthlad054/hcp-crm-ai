import { configureStore } from "@reduxjs/toolkit";
import interactionsReducer from "./slices/interactionsSlice";
import chatReducer from "./slices/chatSlice";
import formReducer from "./slices/formSlice";

export const store = configureStore({
  reducer: {
    interactions: interactionsReducer,
    chat: chatReducer,
    form: formReducer,
  },
});
