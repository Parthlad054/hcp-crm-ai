import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { createInteraction } from "../../redux/slices/interactionsSlice";
import { setFormField, resetForm } from "../../redux/slices/formSlice";
import apiClient from "../../api/client";
import AIAssistant from "./AIAssistant";

const CHANNELS = ["in-person", "call", "email", "conference"];
const SENTIMENTS = ["positive", "neutral", "negative"];

const LogScreen = () => {
  const dispatch = useDispatch();
  const { status } = useSelector((state) => state.interactions);
  const form = useSelector((state) => state.form);
  const isAiFilled = form.isAiFilled;

  const [submitStatus, setSubmitStatus] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    dispatch(
      setFormField({ name, value: type === "checkbox" ? checked : value })
    );
    setSubmitStatus(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.hcp_name.trim()) {
      setSubmitStatus("no_hcp");
      return;
    }

    try {
      const { data: hcpResults } = await apiClient.get("/hcps/", {
        params: { q: form.hcp_name.trim() },
      });

      let hcpId;

      if (hcpResults.length > 0) {
        hcpId = hcpResults[0].id;
      } else {
        const { data: newHcp } = await apiClient.post("/hcps/", {
          name: form.hcp_name.trim(),
        });
        hcpId = newHcp.id;
      }

      const payload = {
        hcp_id: hcpId,
        rep_id: "demo_rep",
        interaction_date: form.interaction_date,
        channel: form.channel,
        sentiment: form.sentiment,
        topics_discussed: form.topics_discussed
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        products_discussed: form.products_discussed
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        summary: form.summary,
        samples_given: form.samples_given || {},
        raw_input: "Manual / AI-Assisted Entry",
        source: "form",
        follow_up_required: form.follow_up_required,
        follow_up_date: form.follow_up_date || null,
      };

      const result = await dispatch(createInteraction(payload));
      if (createInteraction.fulfilled.match(result)) {
        setSubmitStatus("success");
        dispatch(resetForm());
      } else {
        setSubmitStatus("error");
      }
    } catch {
      setSubmitStatus("error");
    }
  };

  const hl = (field) => (isAiFilled && form[field] ? "ai-highlight" : "");

  return (
    <div className="log-screen">
      <div className="log-form-panel glass-panel">
        <div className="log-form-header">
          <h2 className="log-form-title">Log HCP Interaction</h2>
          {isAiFilled && (
            <span className="ai-filled-badge">✨ AI Auto-Filled</span>
          )}
        </div>

        <form onSubmit={handleSubmit} className="log-form">
          <div className="form-section">
            <div className="form-section-label">Interaction Details</div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="hcp_name">HCP Name</label>
                <input
                  id="hcp_name"
                  type="text"
                  name="hcp_name"
                  value={form.hcp_name}
                  onChange={handleChange}
                  placeholder="e.g. Dr. Meera Iyer"
                  className={hl("hcp_name")}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="channel">Interaction Type</label>
                <select
                  id="channel"
                  name="channel"
                  value={form.channel}
                  onChange={handleChange}
                  className={hl("channel")}
                >
                  {CHANNELS.map((c) => (
                    <option key={c} value={c}>
                      {c.charAt(0).toUpperCase() + c.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="interaction_date">Date</label>
                <input
                  id="interaction_date"
                  type="date"
                  name="interaction_date"
                  value={form.interaction_date}
                  onChange={handleChange}
                  className={hl("interaction_date")}
                />
              </div>
              <div className="form-group">
                <label htmlFor="sentiment">Sentiment</label>
                <select
                  id="sentiment"
                  name="sentiment"
                  value={form.sentiment}
                  onChange={handleChange}
                  className={hl("sentiment")}
                >
                  {SENTIMENTS.map((s) => (
                    <option key={s} value={s}>
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <div className="form-group">
              <label htmlFor="topics_discussed">Topics Discussed</label>
              <textarea
                id="topics_discussed"
                name="topics_discussed"
                rows={2}
                value={form.topics_discussed}
                onChange={handleChange}
                placeholder="e.g. Side effects, Dosage, Clinical trial data..."
                className={hl("topics_discussed")}
              />
            </div>

            <div className="form-group">
              <label htmlFor="products_discussed">Materials Shared / Products</label>
              <input
                id="products_discussed"
                type="text"
                name="products_discussed"
                value={form.products_discussed}
                onChange={handleChange}
                placeholder="e.g. Neurocalm, HealPill..."
                className={hl("products_discussed")}
              />
            </div>

            <div className="form-group">
              <label htmlFor="summary">Summary / Notes</label>
              <textarea
                id="summary"
                name="summary"
                rows={3}
                value={form.summary}
                onChange={handleChange}
                placeholder="Brief notes about the meeting..."
                className={hl("summary")}
              />
            </div>
          </div>

          <div className="form-section">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="follow_up_required"
                checked={form.follow_up_required}
                onChange={handleChange}
              />
              <span>Follow-up Required</span>
            </label>
            {form.follow_up_required && (
              <div className="form-group" style={{ marginTop: "0.75rem" }}>
                <label htmlFor="follow_up_date">Follow-up Date</label>
                <input
                  id="follow_up_date"
                  type="date"
                  name="follow_up_date"
                  value={form.follow_up_date}
                  onChange={handleChange}
                  className={hl("follow_up_date")}
                />
              </div>
            )}
          </div>

          {submitStatus === "success" && (
            <div className="form-status success">
              ✅ Interaction logged successfully!
            </div>
          )}
          {submitStatus === "error" && (
            <div className="form-status error">
              ❌ Failed to save. Please try again.
            </div>
          )}
          {submitStatus === "no_hcp" && (
            <div className="form-status error">
              ❌ Please enter an HCP name before submitting.
            </div>
          )}

          <button
            type="submit"
            className="primary-btn submit-btn"
            disabled={status === "loading"}
          >
            {status === "loading" ? "Saving..." : "Log Interaction"}
          </button>
        </form>
      </div>

      <AIAssistant />
    </div>
  );
};

export default LogScreen;
