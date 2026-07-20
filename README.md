# AI-Powered Healthcare CRM

AI-first CRM for pharmaceutical field reps to log Healthcare Professional (HCP) interactions.

Describe a visit in natural language on the right; the LangGraph agent fills and edits the structured form on the left. You should not fill the form manually — the AI assistant drives it.

---

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | React + Redux Toolkit + Vite |
| Backend | Python + FastAPI |
| AI agent | LangGraph + Groq (`llama-3.3-70b-versatile`, fallback `llama-3.1-8b-instant`) |
| Database | PostgreSQL |
| Font | Google Inter |

---

## How it works

```
User message (chat)
       │
       ▼
 POST /chat/  { message, current_form_state }
       │
       ▼
 LangGraph agent (router → tool → response)
       │
       ├── log_interaction      → fill form (+ optional DB save)
       ├── edit_interaction     → selective field patch only
       ├── fetch_hcp_history    → history reply (+ optional hcp_name)
       ├── schedule_follow_up   → follow-up reply (+ form dates)
       └── suggest_talking_points → topics suggestion
       │
       ▼
 { reply, form_data }  → chat bubble + merge into left form
```

**UI layout:** split screen — interaction form on the left, AI chat on the right.

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (Docker recommended)
- A [Groq API key](https://console.groq.com/)

---

## Setup

### 1. Start PostgreSQL (Docker)

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

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

# Create env file and add your Groq key
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux
```

Edit `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:devpass@localhost:5432/hcp_crm
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_MODEL_FALLBACK=llama-3.1-8b-instant
```

Apply migrations and seed sample HCPs/products:

```bash
alembic upgrade head
python seed_db.py
```

Start the API:

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000  
- Swagger docs: http://localhost:8000/docs  
- Health check: http://localhost:8000/health  

### 3. Frontend

```bash
cd frontend
npm install

# Optional: point at a different API URL
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux

npm run dev
```

App: http://localhost:5173  

`frontend/.env` (optional):

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Environment variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `GROQ_API_KEY` | Yes | Groq API token |
| `GROQ_MODEL` | No | Primary model (default: `llama-3.3-70b-versatile`) |
| `GROQ_MODEL_FALLBACK` | No | Fallback / lighter model (default: `llama-3.1-8b-instant`) |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|---|---|---|
| `VITE_API_BASE_URL` | No | Backend base URL (default: `http://localhost:8000`) |

---

## LangGraph tools

| Tool | Purpose |
|---|---|
| `log_interaction` | Extract fields from free text and fill the left form (also saves when HCP matches) |
| `edit_interaction` | Apply a **partial** update using current form state — only mentioned fields change |
| `fetch_hcp_history` | Return recent interactions / sentiment / open follow-ups |
| `schedule_follow_up` | Parse and schedule a follow-up; sets follow-up fields on the form |
| `suggest_talking_points` | Generate visit prep talking points; can pre-fill Topics Discussed |

All form changes are returned as `form_data` from `POST /chat/`. There is no separate `/extract` path — everything goes through LangGraph.

---

## Quick usage examples

1. **Fill the form**  
   Chat: `Met Dr. Smith today, discussed HealPill side effects, sentiment was neutral, no samples.`

2. **Selective edit** (other fields stay the same)  
   Chat: `Sorry, the name was actually Dr. John and the sentiment was negative.`

3. **Save**  
   Review the left panel, then click **Log Interaction**.

---

## Project structure

```
hcp-crm-ai/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph graph, tools, schemas
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routers/        # FastAPI routes (/chat, /interactions, /hcps, …)
│   │   └── main.py
│   ├── alembic/            # DB migrations
│   ├── seed_db.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/LogScreen/   # Form (left) + AIAssistant (right)
    │   ├── redux/                  # form, chat, interactions slices
    │   └── api/client.js
    └── package.json
```

---

## Notes

- No authentication yet — `rep_id` is hardcoded as `demo_rep` for the demo.
- Chat responses are request/response (not streamed).
- Restart the backend after changing `.env` values.
