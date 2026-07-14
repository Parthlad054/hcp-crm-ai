# AI-First CRM — HCP Module: "Log Interaction Screen"
## Implementation Plan

---

## 1. Understanding & Scope

Field reps visit doctors (HCPs) and need to log what happened — who they saw, what was
discussed, samples given, follow-ups needed. The ask is to make this **AI-first**: instead
of only filling a rigid form, a rep can just *talk* to an agent ("Met Dr. Rao today, discussed
Cardixin dosing, she asked for the Phase III data, follow up in 2 weeks") and the agent
extracts structured data automatically — while a structured form remains available as a
fallback/alternate path.

Core deliverable = **one screen, two input modes, one LangGraph agent behind both.**

---

## 2. System Architecture

```
┌─────────────────────────────┐
│  React + Redux Frontend      │
│  - Log Interaction Screen    │
│    ├─ Structured Form Tab    │
│    └─ Chat Interface Tab     │
│  - Interaction History List  │
└───────────┬──────────────────┘
            │ REST (FastAPI)
┌───────────▼──────────────────┐
│  FastAPI Backend              │
│  - /interactions (CRUD)       │
│  - /chat (agent endpoint)     │
│  - /hcps (lookup)              │
└───────────┬──────────────────┘
            │
┌───────────▼──────────────────┐
│  LangGraph Agent               │
│  - Router node                 │
│  - Tool nodes (x5)             │
│  - LLM: Groq gemma2-9b-it       │
└───────────┬──────────────────┘
            │
┌───────────▼──────────────────┐
│  Postgres / MySQL              │
│  - hcps, interactions,          │
│    products, follow_ups         │
└────────────────────────────────┘
```

**Why this shape:** the chat tab and the form tab both ultimately call the *same* backend
tools (Log Interaction, Edit Interaction, etc.) — the form just fills tool arguments
directly without needing the LLM to extract them from free text. This avoids duplicate
business logic and is an easy thing to point out in your video as a design decision.

---

## 3. Tech Stack & Key Decisions

| Layer | Choice | Notes |
|---|---|---|
| Frontend | React + Redux Toolkit | Redux slice per domain: `interactions`, `chat`, `hcps` |
| Styling | Google Inter font, simple design system | Keep clean, don't over-engineer UI polish |
| Backend | FastAPI | Async endpoints, Pydantic schemas mirror DB models |
| Agent | LangGraph | StateGraph with a router + 5 tool nodes |
| LLM | Groq `gemma2-9b-it` (primary) | Fast, cheap — good for extraction/summarization tasks |
| LLM (context/fallback) | `llama-3.3-70b-versatile` | Use for more complex reasoning steps, e.g. talking-point suggestions, if you want to show tiered model usage |
| DB | Postgres (recommended over MySQL for JSONB support — useful for storing flexible extracted-entity payloads) | |
| Auth | Skip or stub (out of scope) — mention as "future work" in README |

---

## 4. Data Model (Postgres)

```sql
hcps (
  id, name, specialty, hospital_affiliation,
  last_interaction_date, notes
)

interactions (
  id, hcp_id FK, rep_id, interaction_date,
  channel (in-person/call/email), topics_discussed TEXT[],
  products_discussed TEXT[], sentiment (positive/neutral/negative),
  samples_given JSONB, follow_up_required BOOL,
  follow_up_date, raw_input TEXT,   -- original chat/form input
  summary TEXT,                     -- LLM-generated
  source (form/chat), created_at, updated_at
)

products ( id, name, category )

follow_ups ( id, interaction_id FK, due_date, status, note )
```

`raw_input` + `summary` stored side by side is a good talking point for the video — shows
you kept the original human input alongside the AI-derived structure (auditability, which
matters a lot in a life-sciences/compliance context).

---

## 5. LangGraph Agent Design

### Role of the agent
The agent is the **single reasoning layer** between "a rep said/typed something" and
"a structured, validated interaction record exists in the DB." It decides *which tool*
to invoke based on user intent (log new / edit existing / look up history / schedule
follow-up / get suggestions), and uses the LLM inside tools that need language
understanding (extraction, summarization).

### Graph shape
- **Entry / Router node**: classifies intent from the incoming message → routes to the
  right tool node (this can literally be an LLM call with a small classification prompt,
  or LangGraph's tool-calling agent pattern where the LLM picks the tool itself — the
  latter is simpler to implement and demo).
- **Tool nodes** (below)
- **Response node**: formats tool output back into a chat reply.

### The 5 Tools

**1. `log_interaction` (mandatory)**
- Input: raw free text (chat) or structured payload (form)
- If chat: calls Groq gemma2-9b-it with a prompt to extract entities — HCP name, date,
  topics, products mentioned, sentiment, samples given, follow-up need — as JSON
- Validates HCP exists (fuzzy-matches against `hcps` table; asks for clarification if
  ambiguous — good demo moment)
- Calls LLM again (or same call) to produce a short human-readable `summary`
- Inserts row into `interactions`
- Returns confirmation + summary to the rep

**2. `edit_interaction` (mandatory)**
- Input: interaction ID (or "my last log with Dr. X") + the change requested in natural
  language, e.g. "change the date to yesterday" or "add that she wants literature"
- Agent fetches the existing record, sends old record + requested change to the LLM,
  gets back a diff/patch (structured JSON), applies it, re-generates `summary`
- Returns before/after so the rep can confirm — shows the agent isn't silently mutating data

**3. `fetch_hcp_history`**
- Input: HCP name
- Returns past interactions, last visit date, sentiment trend, open follow-ups
- Useful before a visit ("what did we last discuss with Dr. Rao?")

**4. `schedule_follow_up`**
- Input: interaction ID or HCP name + follow-up detail ("remind me in 2 weeks to send
  the trial data")
- Parses relative date via LLM, writes to `follow_ups` table
- Could optionally surface on a dashboard (not required, but nice extra)

**5. `suggest_talking_points`**
- Input: HCP name (+ optionally a product name)
- Pulls HCP history + product info, asks the (larger, llama-3.3-70b-versatile) LLM to
  suggest 2-3 relevant discussion points for the *next* visit
- This is the tool that most clearly demonstrates "AI-first" value beyond pure data entry —
  good one to lead with in the video demo

> Tip: pick a 6th tool only if time allows (e.g. `flag_compliance_risk` — scans summary
> for off-label language). Five is the minimum required; don't over-scope given the clock.

---

## 6. Frontend Structure (React + Redux)

```
src/
  components/
    LogInteractionScreen/
      FormView.jsx
      ChatView.jsx
      ModeToggle.jsx
    InteractionHistory/
      HCPHistoryList.jsx
    shared/
  redux/
    slices/
      interactionsSlice.js
      chatSlice.js
      hcpSlice.js
    store.js
  api/
    client.js   // axios/fetch wrapper to FastAPI
  App.jsx
```

- `ModeToggle` switches between Form and Chat — both write to the same
  `interactionsSlice` via the same backend endpoint pattern.
- Chat view: simple message list + input, streaming not required (keep simple — a
  single request/response per turn is fine given the time budget).
- Use Google Inter via `@fontsource/inter` or Google Fonts CDN link.

---

## 7. FastAPI Endpoints (minimum set)

```
POST   /chat                  → routes message into LangGraph agent
POST   /interactions           → create via structured form (bypasses NLU, calls log_interaction tool directly with structured args)
GET    /interactions/{hcp_id}  → history
PATCH  /interactions/{id}      → edit
POST   /follow-ups              → schedule
GET    /hcps                    → lookup/autocomplete
```

---

## 8. Suggested 36-Hour Timeline

| Hours | Task |
|---|---|
| 0–3 | Repo scaffold, DB schema, FastAPI skeleton, Groq API key test call |
| 3–9 | Build LangGraph agent + all 5 tools against a stub DB; test each tool via script/Postman before touching frontend |
| 9–14 | Connect agent to real Postgres; test log → edit → history flow end-to-end via API |
| 14–22 | React + Redux frontend: form view, chat view, wire to backend |
| 22–26 | Styling pass (Inter font, clean layout), polish chat UX |
| 26–29 | Full end-to-end test of all 5 tools through the UI; fix bugs |
| 29–31 | Write README (setup, architecture, tool descriptions) |
| 31–35 | Record 10–15 min video (script it first — see below) |
| 35–36 | Push final repo, fill Google Form, submit |

---

## 9. README Checklist

- Project overview (1 paragraph, same as your "understanding" summary)
- Architecture diagram (reuse the one above)
- Setup instructions: env vars (`GROQ_API_KEY`, `DATABASE_URL`), `pip install`,
  `npm install`, migration commands, run commands for backend + frontend
- List of the 5 tools with one-line description each
- Known limitations / future work (auth, streaming chat, compliance flagging, etc.)

## 10. Video Script Outline (10–15 min)

1. **(1 min)** What you understood the task to be
2. **(3 min)** Frontend walkthrough — show form mode, then chat mode logging the same
   kind of interaction, compare
3. **(6–8 min)** Demo all 5 tools explicitly, naming each one as you trigger it
   (log → edit → history → follow-up → suggest talking points)
4. **(2 min)** Code structure tour — LangGraph graph file, tool definitions, one Redux
   slice, one FastAPI route
5. **(1 min)** Wrap-up / design tradeoffs you'd tackle with more time

---

## 11. Notes on Using AI Coding Tools (per task instructions)

Since zero hand-written code is expected and Gemini/ChatGPT are sanctioned for this,
your highest-leverage move is writing **very specific prompts per tool/component**
(e.g., "write the LangGraph tool node for `edit_interaction` that takes {schema} and
calls Groq gemma2-9b-it to produce a JSON patch") rather than asking for the whole app
in one prompt — you'll get more correct, reviewable output and it'll be easier to explain
in the video since you'll actually understand each piece.
