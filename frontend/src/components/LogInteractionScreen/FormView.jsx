import React, { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { createInteraction } from "../../redux/slices/interactionsSlice";

const FormView = () => {
  const dispatch = useDispatch();
  const { selectedHCP } = useSelector((state) => state.hcps);
  
  const [formData, setFormData] = useState({
    interaction_date: new Date().toISOString().split("T")[0],
    channel: "in-person",
    sentiment: "neutral",
    topics_discussed: "",
    products_discussed: "",
    summary: "",
    follow_up_required: false,
    follow_up_date: "",
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedHCP) {
      alert("Please select an HCP first!");
      return;
    }

    const payload = {
      hcp_id: selectedHCP.id,
      rep_id: "demo_rep",
      interaction_date: formData.interaction_date,
      channel: formData.channel,
      sentiment: formData.sentiment,
      topics_discussed: formData.topics_discussed.split(",").map((s) => s.trim()).filter(Boolean),
      products_discussed: formData.products_discussed.split(",").map((s) => s.trim()).filter(Boolean),
      summary: formData.summary,
      raw_input: "Manual Form Entry",
      source: "form",
      follow_up_required: formData.follow_up_required,
      follow_up_date: formData.follow_up_date || null,
    };

    dispatch(createInteraction(payload));
    
    setFormData({
      ...formData,
      topics_discussed: "",
      products_discussed: "",
      summary: "",
      follow_up_required: false,
      follow_up_date: "",
    });
    alert("Interaction logged successfully!");
  };

  if (!selectedHCP) {
    return <div className="form-empty-state glass-panel">Please select an HCP from the sidebar to log an interaction.</div>;
  }

  return (
    <form className="form-view glass-panel" onSubmit={handleSubmit}>
      <h2 className="form-title">Log Interaction for {selectedHCP.name}</h2>
      
      <div className="form-row">
        <div className="form-group">
          <label>Date</label>
          <input type="date" name="interaction_date" value={formData.interaction_date} onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>Channel</label>
          <select name="channel" value={formData.channel} onChange={handleChange}>
            <option value="in-person">In-Person</option>
            <option value="call">Call</option>
            <option value="email">Email</option>
          </select>
        </div>
        <div className="form-group">
          <label>Sentiment</label>
          <select name="sentiment" value={formData.sentiment} onChange={handleChange}>
            <option value="positive">Positive</option>
            <option value="neutral">Neutral</option>
            <option value="negative">Negative</option>
          </select>
        </div>
      </div>

      <div className="form-group">
        <label>Topics Discussed (comma separated)</label>
        <input type="text" name="topics_discussed" placeholder="e.g. Side effects, Dosage..." value={formData.topics_discussed} onChange={handleChange} />
      </div>

      <div className="form-group">
        <label>Products Discussed (comma separated)</label>
        <input type="text" name="products_discussed" placeholder="e.g. WonderDrug, HealPill..." value={formData.products_discussed} onChange={handleChange} />
      </div>

      <div className="form-group">
        <label>Summary</label>
        <textarea name="summary" rows="3" placeholder="Brief notes about the meeting..." value={formData.summary} onChange={handleChange} required></textarea>
      </div>

      <div className="form-row follow-up-row">
        <label className="checkbox-label">
          <input type="checkbox" name="follow_up_required" checked={formData.follow_up_required} onChange={handleChange} />
          Follow-up Required
        </label>
        {formData.follow_up_required && (
          <input type="date" name="follow_up_date" value={formData.follow_up_date} onChange={handleChange} required />
        )}
      </div>
      
      <button type="submit" className="submit-btn primary-btn">Log Interaction</button>
    </form>
  );
};

export default FormView;
