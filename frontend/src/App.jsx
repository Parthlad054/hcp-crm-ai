import React from "react";
import LogScreen from "./components/LogScreen/LogScreen";
import "./App.css";

function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-brand">
          <span className="header-logo">⚕️</span>
          <div>
            <h1 className="header-title">HCP CRM AI</h1>
            <span className="header-sub">Life Sciences Field CRM</span>
          </div>
        </div>
        <div className="header-right">
          <div className="rep-badge">
            <span className="rep-avatar">P</span>
            <span className="rep-name">Demo Rep</span>
          </div>
        </div>
      </header>

      {/* Full width — no sidebar */}
      <main className="app-main">
        <LogScreen />
      </main>
    </div>
  );
}

export default App;
