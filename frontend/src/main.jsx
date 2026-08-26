import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import { store } from "./redux/store";
import App from "./App";
import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";
import "./index.css";

// ── One-time migration: remove the old combined localStorage key ──────────────
// The previous store stored auth + UI in "hcp_crm_state". We now split them
// into "hcp_crm_auth" (sessionStorage) and "hcp_crm_ui" (localStorage).
// Removing the old key prevents stale phantom sessions for existing users.
localStorage.removeItem("hcp_crm_state");

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);
