import React, { useState } from "react";
import HCPSelector from "./components/shared/HCPSelector";
import HCPHistoryList from "./components/InteractionHistory/HCPHistoryList";
import ModeToggle from "./components/LogInteractionScreen/ModeToggle";
import FormView from "./components/LogInteractionScreen/FormView";
import ChatView from "./components/LogInteractionScreen/ChatView";
import "./App.css";

function App() {
  const [mode, setMode] = useState("chat"); // 'chat' or 'form'

  return (
    <div className="app-shell">
      <header className="app-header glass-panel">
        <div className="header-left">
          <span className="app-logo">⚕️</span>
          <h1 className="app-title">HCP CRM AI</h1>
        </div>
        <div className="header-right">
          <span className="user-profile">Dr. Rep</span>
        </div>
      </header>
      
      <main className="app-main">
        <aside className="app-sidebar">
          <HCPSelector />
          <HCPHistoryList />
        </aside>
        
        <section className="app-content">
          <ModeToggle mode={mode} setMode={setMode} />
          <div className="view-container">
            {mode === "form" ? <FormView /> : <ChatView />}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
