import { createSlice } from "@reduxjs/toolkit";

const emptyForm = {
  hcp_name: "",
  interaction_date: new Date().toISOString().split("T")[0],
  channel: "in-person",
  sentiment: "neutral",
  topics_discussed: "",
  products_discussed: "",
  summary: "",
  samples_given: {},
  follow_up_required: false,
  follow_up_date: "",
};

/** Map API form_data (uses `date`) into local form fields. Only set keys that are present. */
function applyFormData(state, data) {
  if (!data || typeof data !== "object") return;

  if ("hcp_name" in data && data.hcp_name != null) state.hcp_name = data.hcp_name;
  if ("date" in data || "interaction_date" in data) {
    const d = data.date ?? data.interaction_date;
    if (d != null) state.interaction_date = d;
  }
  if ("channel" in data && data.channel != null) state.channel = data.channel;
  if ("sentiment" in data && data.sentiment != null) state.sentiment = data.sentiment;

  if ("topics_discussed" in data && data.topics_discussed != null) {
    state.topics_discussed = Array.isArray(data.topics_discussed)
      ? data.topics_discussed.join(", ")
      : String(data.topics_discussed);
  }
  if ("products_discussed" in data && data.products_discussed != null) {
    state.products_discussed = Array.isArray(data.products_discussed)
      ? data.products_discussed.join(", ")
      : String(data.products_discussed);
  }
  if ("summary" in data && data.summary != null) state.summary = data.summary;
  if ("samples_given" in data && data.samples_given != null) {
    state.samples_given = data.samples_given;
  }
  if ("follow_up_required" in data && data.follow_up_required != null) {
    state.follow_up_required = data.follow_up_required;
  }
  if ("follow_up_date" in data) {
    state.follow_up_date = data.follow_up_date || "";
  }
}

const formSlice = createSlice({
  name: "form",
  initialState: {
    ...emptyForm,
    isAiFilled: false,
  },
  reducers: {
    setFormField(state, action) {
      const { name, value } = action.payload;
      state[name] = value;
      state.isAiFilled = false;
    },
    mergeFormData(state, action) {
      applyFormData(state, action.payload);
      state.isAiFilled = true;
    },
    resetForm(state) {
      Object.assign(state, emptyForm, {
        interaction_date: new Date().toISOString().split("T")[0],
        isAiFilled: false,
      });
    },
  },
});

export const { setFormField, mergeFormData, resetForm } = formSlice.actions;

/** Shape sent to POST /chat as current_form_state */
export const selectCurrentFormState = (state) => {
  const f = state.form;
  return {
    hcp_name: f.hcp_name || null,
    date: f.interaction_date || null,
    channel: f.channel || null,
    products_discussed: f.products_discussed
      ? f.products_discussed.split(",").map((s) => s.trim()).filter(Boolean)
      : [],
    topics_discussed: f.topics_discussed
      ? f.topics_discussed.split(",").map((s) => s.trim()).filter(Boolean)
      : [],
    sentiment: f.sentiment || null,
    samples_given: f.samples_given || {},
    follow_up_required: f.follow_up_required,
    follow_up_date: f.follow_up_date || null,
    summary: f.summary || null,
  };
};

export default formSlice.reducer;
