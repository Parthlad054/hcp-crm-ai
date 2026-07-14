# Phase 1: Project Scaffold & Database Setup
### (Hours 0–3 of the 36-Hour Plan — AI-First CRM HCP Module)

This document covers the exact scaffold to set up before writing any agent/tool logic:
repo layout, backend skeleton, frontend skeleton, database schema (from the master plan,
unchanged), environment configuration, and the Groq API connectivity check.

---

## 1. Repository Structure (Monorepo)

One GitHub repo, two top-level app folders, as required by the deliverable ("frontend
and backend code in one GitHub repository").

```
hcp-crm-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entrypoint
│   │   ├── config.py               # env var loading (Groq key, DB url)
│   │   ├── database.py             # SQLAlchemy engine/session
│   │   ├── models/
│   │   │   ├── hcp.py
│   │   │   ├── interaction.py
│   │   │   ├── product.py
│   │   │   └── follow_up.py
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   │   ├── hcp.py
│   │   │   ├── interaction.py
│   │   │   └── follow_up.py
│   │   ├── routers/
│   │   │   ├── interactions.py
│   │   │   ├── chat.py
│   │   │   ├── hcps.py
│   │   │   └── follow_ups.py
│   │   ├── agent/                  # LangGraph agent (Phase 2 work)
│   │   │   ├── graph.py
│   │   │   └── tools/
│   │   └── llm/
│   │       └── groq_client.py
│   ├── alembic/                    # DB migrations
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile (optional)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LogInteractionScreen/
│   │   │   ├── InteractionHistory/
│   │   │   └── shared/
│   │   ├── redux/
│   │   │   ├── slices/
│   │   │   └── store.js
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── .env.example
│
├── README.md
└── .gitignore
```

---

## 2. Database Setup (Postgres)

Chosen over MySQL per the master plan's rationale (JSONB support for flexible
extracted-entity fields like `samples_given`).

### 2.1 Local setup
```bash
# via Docker (fastest path for a 36-hour build)
docker run --name hcp-crm-db -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=hcp_crm -p 5432:5432 -d postgres:16
```

### 2.2 Schema (`alembic` migration or raw SQL — identical to master plan §4)

```sql
CREATE TABLE hcps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(255),
    hospital_affiliation VARCHAR(255),
    last_interaction_date DATE,
    notes TEXT
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255)
);

CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    hcp_id INTEGER REFERENCES hcps(id),
    rep_id VARCHAR(255),
    interaction_date DATE NOT NULL,
    channel VARCHAR(50),                 -- in-person / call / email
    topics_discussed TEXT[],
    products_discussed TEXT[],
    sentiment VARCHAR(50),               -- positive / neutral / negative
    samples_given JSONB,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date DATE,
    raw_input TEXT,                      -- original chat/form input
    summary TEXT,                        -- LLM-generated
    source VARCHAR(20),                  -- form / chat
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE follow_ups (
    id SERIAL PRIMARY KEY,
    interaction_id INTEGER REFERENCES interactions(id),
    due_date DATE,
    status VARCHAR(50) DEFAULT 'pending',
    note TEXT
);
```

### 2.3 Alembic init (recommended over raw SQL for a "professional" repo)
```bash
cd backend
alembic init alembic
# point alembic.ini / env.py at DATABASE_URL from .env
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

---

## 3. Backend Skeleton (FastAPI)

### 3.1 `requirements.txt`
```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
alembic
pydantic
python-dotenv
langgraph
langchain-groq
groq
```

### 3.2 `.env.example`
```
DATABASE_URL=postgresql://postgres:devpass@localhost:5432/hcp_crm
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=gemma2-9b-it
GROQ_MODEL_FALLBACK=llama-3.3-70b-versatile
```

### 3.3 `app/main.py` (skeleton)
```python
from fastapi import FastAPI
from app.routers import interactions, chat, hcps, follow_ups

app = FastAPI(title="AI-First CRM — HCP Module")

app.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(hcps.router, prefix="/hcps", tags=["hcps"])
app.include_router(follow_ups.router, prefix="/follow-ups", tags=["follow-ups"])

@app.get("/health")
def health():
    return {"status": "ok"}
```

### 3.4 Groq connectivity check (`app/llm/groq_client.py`)
Run this as a standalone smoke test before building agent logic — confirms the API key
and model name work before anything else depends on it.
```python
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def test_connection():
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "gemma2-9b-it"),
        messages=[{"role": "user", "content": "Reply with OK if you can read this."}],
    )
    print(response.choices[0].message.content)

if __name__ == "__main__":
    test_connection()
```
```bash
python -m app.llm.groq_client   # expect "OK" printed back
```

---

## 4. Frontend Skeleton (React + Redux)

### 4.1 Scaffold
```bash
npx create-react-app frontend
cd frontend
npm install @reduxjs/toolkit react-redux axios @fontsource/inter
```

### 4.2 `src/index.js` — Inter font import
```javascript
import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";
```

### 4.3 `src/redux/store.js`
```javascript
import { configureStore } from "@reduxjs/toolkit";
import interactionsReducer from "./slices/interactionsSlice";
import chatReducer from "./slices/chatSlice";
import hcpReducer from "./slices/hcpSlice";

export const store = configureStore({
  reducer: {
    interactions: interactionsReducer,
    chat: chatReducer,
    hcps: hcpReducer,
  },
});
```

### 4.4 `.env.example`
```
REACT_APP_API_BASE_URL=http://localhost:8000
```

---

## 5. `.gitignore` (root)
```
# backend
__pycache__/
*.pyc
.env
venv/

# frontend
node_modules/
build/

# db
*.sqlite3
```

---

## 6. Verification Checklist Before Moving to Phase 2 (Agent Build)

- [ ] `docker ps` shows Postgres running
- [ ] `alembic upgrade head` runs clean, tables visible via `psql` or a client (e.g. TablePlus/DBeaver)
- [ ] `uvicorn app.main:app --reload` starts, `/health` returns `{"status": "ok"}`
- [ ] Groq smoke test script prints a response (confirms API key + model name valid)
- [ ] `npm start` in `frontend/` loads a blank CRA page with no console errors
- [ ] Repo pushed to GitHub with this folder structure in place (empty stub files are fine for now)

Once every box above is checked, move to **Phase 2: LangGraph Agent + 5 Tools**, per the
master plan's Hours 3–9 block.
