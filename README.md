# AI-First CRM — HCP Module

> A LangGraph-powered CRM for field reps to log Healthcare Professional (HCP) interactions via natural language chat **or** a structured form — both backed by the same AI agent.

---

## Architecture

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
│  - /hcps (lookup)             │
└───────────┬──────────────────┘
            │
┌───────────▼──────────────────┐
│  LangGraph Agent              │
│  - Router node                │
│  - Tool nodes (x5)            │
│  - LLM: Groq gemma2-9b-it    │
└───────────┬──────────────────┘
            │
┌───────────▼──────────────────┐
│  PostgreSQL                   │
│  - hcps, interactions,        │
│    products, follow_ups       │
└───────────────────────────────┘
```

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for Postgres) or a local Postgres instance

### 1. Start Postgres (Docker)
```bash
docker run --name hcp-crm-db \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=hcp_crm \
  -p 5432:5432 -d postgres:16
```

### 2. Backend
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Copy and fill in your env vars
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux

# Run DB migrations
alembic init alembic          # first time only
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### 3. Groq API Key Smoke Test
```bash
python -m app.llm.groq_client
# Expected output: [Groq smoke test] Model: gemma2-9b-it | Response: OK
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `GROQ_API_KEY` | Your Groq API key |
| `GROQ_MODEL` | Primary model (default: `llama-3.3-70b-versatile`) |
| `GROQ_MODEL_FALLBACK` | Fallback model (default: `llama-3.1-8b-instant`) |

---

## LangGraph Agent Tools

| Tool | Description |
|---|---|
| `log_interaction` | Extracts structured data from free-text chat and persists a new interaction record |
| `edit_interaction` | Applies natural-language change requests to an existing interaction |
| `fetch_hcp_history` | Returns past interactions, sentiment trend, and open follow-ups for an HCP |
| `schedule_follow_up` | Parses a relative-date follow-up request and writes it to the DB |
| `suggest_talking_points` | Uses the larger LLM to generate personalised visit prep suggestions |

---

## Known Limitations / Future Work
- **Auth**: No authentication — marked as future work. Rep identity is passed as `rep_id` string.
- **Streaming chat**: Single request/response per turn; streaming responses not yet implemented.
- **Compliance flagging**: A 6th tool (`flag_compliance_risk`) is referenced in the plan but out of scope for this build.
- **Relative dates**: Follow-up date parsing depends on LLM accuracy; edge cases not exhaustively tested.
