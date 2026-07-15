import React, { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { sendChatMessage, addUserMessage } from "../../redux/slices/chatSlice";
import { fetchInteractions } from "../../redux/slices/interactionsSlice";

const ChatView = () => {
  const dispatch = useDispatch();
  const { messages, status, sessionId } = useSelector((state) => state.chat);
  const { selectedHCP } = useSelector((state) => state.hcps);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const message = input.trim();
    setInput("");
    
    dispatch(addUserMessage(message));
    await dispatch(sendChatMessage({ message, sessionId }));
    
    if (selectedHCP) {
      dispatch(fetchInteractions(selectedHCP.id));
    }
  };

  return (
    <div className="chat-view glass-panel">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <span className="ai-icon">🤖</span>
            <p>Hi! I'm your CRM assistant. Tell me about your recent interaction, ask about an HCP's history, or schedule a follow-up.</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble-container ${msg.role === 'user' ? 'user' : 'agent'}`}>
            <div className={`chat-bubble ${msg.role === 'user' ? 'user-bubble' : 'agent-bubble'}`}>
              {msg.content}
            </div>
          </div>
        ))}
        {status === "loading" && (
          <div className="chat-bubble-container agent">
            <div className="chat-bubble agent-bubble typing-indicator">
              <span>.</span><span>.</span><span>.</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input-area" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Log a meeting, ask for talking points..."
          disabled={status === "loading"}
        />
        <button type="submit" className="primary-btn" disabled={status === "loading" || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatView;
