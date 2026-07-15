import React, { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { sendChatMessage } from "../../redux/slices/chatSlice";
import { selectCurrentFormState } from "../../redux/slices/formSlice";

const WELCOME = {
  role: "assistant",
  content:
    "Hi! I'm your AI assistant. Describe your HCP interaction in plain English and I'll automatically fill in the form on the left.\n\n" +
    'Try: "Visited Dr. Meera Iyer at City Hospital. Discussed Neurocalm, she was hesitant. No samples given."\n\n' +
    'To correct a field later, say e.g. "Sorry, the name was actually Dr. John and the sentiment was negative."',
};

const AIAssistant = () => {
  const dispatch = useDispatch();
  const currentFormState = useSelector(selectCurrentFormState);
  const sessionId = useSelector((s) => s.chat.sessionId);

  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);

    try {
      const result = await dispatch(
        sendChatMessage({
          message: text,
          sessionId,
          currentFormState,
        })
      );

      if (sendChatMessage.fulfilled.match(result)) {
        const reply = result.payload.reply || "Done.";
        setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "Sorry, I couldn't process that. Please try again with the doctor's name and key details.",
          },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, something went wrong reaching the assistant. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const renderContent = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <div className="ai-assistant glass-panel">
      <div className="ai-header">
        <span className="ai-header-icon">🤖</span>
        <div>
          <div className="ai-header-title">AI Assistant</div>
          <div className="ai-header-sub">Describe interaction to auto-fill the form</div>
        </div>
        <div className={`ai-status-dot ${loading ? "pulsing" : "idle"}`} />
      </div>

      <div className="ai-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`ai-bubble-wrap ${msg.role}`}>
            <div className={`ai-bubble ${msg.role}`}>
              {msg.content.split("\n").map((line, i) => (
                <span key={i}>
                  {renderContent(line)}
                  {i < msg.content.split("\n").length - 1 && <br />}
                </span>
              ))}
            </div>
          </div>
        ))}

        {loading && (
          <div className="ai-bubble-wrap assistant">
            <div className="ai-bubble assistant typing">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <form className="ai-input-row" onSubmit={sendMessage}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe interaction here via chat..."
          disabled={loading}
        />
        <button type="submit" className="ai-send-btn" disabled={loading || !input.trim()}>
          {loading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
};

export default AIAssistant;
