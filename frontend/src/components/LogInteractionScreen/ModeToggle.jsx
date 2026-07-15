import React from "react";

const ModeToggle = ({ mode, setMode }) => {
  return (
    <div className="mode-toggle glass-panel">
      <button 
        className={`toggle-btn ${mode === "form" ? "active" : ""}`} 
        onClick={() => setMode("form")}
      >
        📝 Manual Form
      </button>
      <button 
        className={`toggle-btn ${mode === "chat" ? "active" : ""}`} 
        onClick={() => setMode("chat")}
      >
        💬 AI Assistant
      </button>
    </div>
  );
};

export default ModeToggle;
