# 🏥 HCP CRM AI

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?logo=react)](https://react.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20AI-blueviolet.svg)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/Groq-Llama--3-orange.svg)](https://groq.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg?logo=postgresql)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **An AI-First Customer Relationship Management (CRM) platform designed specifically for pharmaceutical and medical device sales representatives.** Transform unstructured post-visit doctor notes into structured, validated CRM records in seconds using autonomous LangGraph agents and fast Groq LLM inference.

---

## 📌 Overview

Pharmaceutical sales representatives routinely spend up to 40% of their day manually inputting clinical meeting notes, compliance details, and follow-up actions across rigid CRM forms. 

**HCP CRM AI** solves this with an agentic copilot:
- Reps simply type or speak their natural language visit notes (e.g., *"Met Dr. Adams at City Clinic, discussed WonderDrug dosing, he was positive and requested samples for next Tuesday"*).
- An intelligent **LangGraph** multi-tool agent automatically extracts clinical entities (HCP name, products, sentiment, dosage discussions, samples, and follow-up dates).
- The agent cross-references the PostgreSQL database, resolves doctors via fuzzy matching, records the visit, and auto-populates the interactive UI in real time.

---

## ✨ Key Features

- **⚡ Conversational Interaction Logging**: Dictate or type free-form notes; the agent extracts clinical topics, products, sentiment, and sample requests automatically.
- **✨ Real-Time Form Auto-Fill**: Extracted entities sync seamlessly with the frontend via Redux Toolkit, featuring visual **"✨ AI Auto-Filled"** indicator badges.
- **🧠 LangGraph State Machine Agent**: Autonomous multi-tool agent powered by Groq (Llama 3) with dynamic tool selection, conversational memory, and structured Pydantic outputs.
- **🔍 Smart HCP Entity Resolution**: Intelligent fuzzy matching resolves doctor identities and clinic affiliations even when names are abbreviated or misspelled.
- **📊 Longitudinal History & Sentiment Insights**: Instant retrieval of historical meetings, sentiment trajectories (positive, neutral, negative), and past discussion topics for pre-call planning.
- **💡 AI-Generated Talking Points**: Dynamically generates personalized conversation starters and clinical talking points based on doctor specialty and visit history.
- **📅 Automatic Follow-Up Task Management**: Schedules reminders and next visits directly from natural language context into dedicated database task queues.
- **🔐 Secure Enterprise Authentication**: Complete JWT authentication lifecycle with access/refresh tokens, password hashing with bcrypt, and SMTP password reset flows.
- **🛡️ Production Ready**: Equipped with SlowAPI rate limiting, TTL in-memory caching, comprehensive Pytest suites, Alembic migrations, and Docker configuration.

---

## 🏗️ Architecture

```mermaid
graph TD
    User([Sales Representative]) -->|Web Browser / UI| Frontend[React 19 + Redux Toolkit]
    Frontend -->|REST API / JWT| Backend[FastAPI Backend]
    
    subgraph Backend Core
        Backend --> Router[API Routers / v1]
        Router --> Auth[Auth & Rate Limiting]
        Router --> AgentBridge[Agent Service Bridge]
    end
    
    subgraph Agentic AI Engine
        AgentBridge --> LG[LangGraph StateGraph]
        LG --> LLM[Groq Cloud / Llama 3]
        LG --> Tools[Domain Agent Tools]
        
        Tools --> Tool1[log_interaction]
        Tools --> Tool2[edit_interaction]
        Tools --> Tool3[fetch_hcp_history]
        Tools --> Tool4[suggest_talking_points]
        Tools --> Tool5[schedule_follow_up]
    end
    
    subgraph Data & Storage
        Tool1 --> DB[(PostgreSQL Database)]
        Tool2 --> DB
        Tool3 --> DB
        Tool4 --> DB
        Tool5 --> DB
        Router --> DB
    end
```

---

## 🤖 Agent Tools & Capabilities

The LangGraph agent acts as an autonomous clinical orchestrator with 5 dedicated tools:

| Tool | Purpose | Example Rep Prompt |
| :--- | :--- | :--- |
| `log_interaction` | Extracts structured visit data, resolves HCP ID, writes log & auto-fills form | *"Met Dr. Adams at Community Health. Discussed WonderDrug efficacy, sentiment was very positive, agreed to follow up in 2 weeks."* |
| `edit_interaction` | Dynamically updates previously extracted form fields without starting over | *"Actually, change the meeting channel to conference and add Neurocalm to discussed products."* |
| `fetch_hcp_history` | Retrieves past visit summaries, sentiment trends, and clinical topics | *"Show me recent visit history and sentiment trend for Dr. Faizal."* |
| `suggest_talking_points` | Analyzes historical logs to propose targeted talking points for upcoming visits | *"What clinical topics should I bring up in my next meeting with Dr. Adams?"* |
| `schedule_follow_up` | Creates task reminders and follow-up alerts tied to specific HCP records | *"Remind me to call Dr. Adams next Tuesday to deliver medication samples."* |

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: [React 19](https://react.dev/) + [Vite](https://vitejs.dev/)
- **State Management**: [Redux Toolkit](https://redux-toolkit.js.org/) + `react-redux`
- **Typography & Styling**: Glassmorphic modern CSS design system + `@fontsource/inter`
- **HTTP Client**: [Axios](https://axios-http.com/) with interceptors for token auto-refresh

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **ORM & DB Migrations**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) & [Alembic](https://alembic.sqlalchemy.org/)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings`
- **Security & Auth**: `python-jose` (JWT), `bcrypt`, `slowapi` (rate limiting)
- **Email Service**: `aiosmtplib` (asynchronous password reset delivery)

### AI & Agent Orchestration
- **Agent Framework**: [LangGraph](https://github.com/langchain-ai/langgraph)
- **Integration**: [LangChain](https://www.langchain.com/) + `langchain-groq`
- **Inference Engine**: [Groq](https://groq.com/) (High-speed Llama 3 models)

### Database & Infrastructure
- **Database**: [PostgreSQL 15+](https://www.postgresql.org/)
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

---

## 📂 Project Structure

```
hcp-crm-ai/
├── backend/
│   ├── alembic/                 # Database migrations (versions & env)
│   ├── app/
│   │   ├── agent/               # LangGraph state machine & AI tools
│   │   │   ├── tools/           # log, edit, history, suggestions, follow-up
│   │   │   ├── graph.py         # StateGraph definition & tool routing
│   │   │   ├── state.py         # Agent state schemas
│   │   │   └── schemas.py       # Pydantic extraction models
│   │   ├── api/v1/              # API endpoints (auth, chat, hcps, interactions)
│   │   ├── core/                # App config, security, rate limiting, error handlers
│   │   ├── models/              # SQLAlchemy database models (HCP, Interaction, User, FollowUp)
│   │   ├── repositories/        # Database queries & repository layer
│   │   ├── schemas/             # Request/response Pydantic schemas
│   │   ├── services/            # Business logic (Auth, Email, HCP services)
│   │   ├── database.py          # SQLAlchemy session engine
│   │   └── main.py              # FastAPI application entrypoint
│   ├── scripts/
│   │   └── seed_db.py           # Seed database with realistic HCP clinical data
│   ├── tests/                   # Test suite (Unit, Integration, Smoke, Performance)
│   ├── docker-compose.yml       # Multi-container orchestration
│   ├── Dockerfile               # Backend production container specification
│   ├── Makefile                 # CLI developer task automation
│   └── requirements.txt         # Python package dependencies
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios client, auth API & chat endpoints
│   │   ├── components/          # UI components (Auth, Form, Chat, History)
│   │   ├── redux/               # Redux slices (auth, chat, interaction form)
│   │   ├── App.jsx              # Main dashboard layout (3-column view)
│   │   └── index.css            # Custom CSS & design token styling
│   └── package.json             # Frontend NPM scripts and dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
- **Python 3.10+**
- **Node.js 18+** & **npm**
- **PostgreSQL 14+** (or use Docker)
- **Groq API Key** (Free tier available at [console.groq.com](https://console.groq.com))

---

### Step 1: Clone Repository

```bash
git clone https://github.com/your-username/hcp-crm-ai.git
cd hcp-crm-ai
```

---

### Step 2: Backend Setup

1. **Navigate to the backend directory & create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your settings:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hcp_crm
   GROQ_API_KEY=gsk_your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   SECRET_KEY=your_super_secret_jwt_key_min_32_chars
   ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
   FRONTEND_URL=http://localhost:5173
   ```

4. **Run database migrations and seed sample HCP data:**
   ```bash
   alembic upgrade head
   python scripts/seed_db.py
   ```

5. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - 🌐 API Server: `http://localhost:8000`
   - 📖 Interactive Swagger Docs: `http://localhost:8000/docs`

---

### Step 3: Frontend Setup

1. **Open a new terminal and navigate to `frontend`:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```
   - 💻 App URL: `http://localhost:5173`

---

## 🐳 Docker Deployment (Alternative)

To spin up the entire application along with PostgreSQL using Docker Compose:

```bash
cd backend
docker-compose up --build -d
```

Containers started:
- `db`: PostgreSQL Database on port `5432`
- `api`: FastAPI application on port `8000`

---

## ⚙️ Environment Variables

| Variable | Description | Default / Example | Required |
| :--- | :--- | :--- | :---: |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/hcp_crm` | Yes |
| `GROQ_API_KEY` | API Key for Groq Cloud LLM inference | `gsk_...` | Yes |
| `GROQ_MODEL` | Primary model for LangGraph agent | `llama-3.3-70b-versatile` | No |
| `SECRET_KEY` | Cryptographic secret for signing JWT tokens | Random string (min 32 chars) | Yes |
| `ALLOWED_ORIGINS` | Permitted CORS frontend origins | `http://localhost:5173` | Yes |
| `FRONTEND_URL` | Public frontend URL for password reset links | `http://localhost:5173` | Yes |
| `SMTP_HOST` | SMTP server for password reset emails | `smtp.gmail.com` | Optional |
| `SMTP_PORT` | SMTP port (typically 587 or 465) | `587` | Optional |
| `SMTP_USERNAME` | SMTP account username / email | `user@example.com` | Optional |
| `SMTP_PASSWORD` | SMTP app password | `app_password` | Optional |

---

## 🧪 Testing & Code Quality

The backend includes a comprehensive test suite executed via `pytest`:

```bash
cd backend

# Run all tests
make test
# or: pytest tests/ -v

# Run fast smoke tests (ideal for CI/CD pipelines)
make test-smoke

# Run unit tests
make test-unit

# Run integration & database tests
make test-integration

# Generate HTML code coverage report
make test-cov

# Run linter & formatter checks
make lint
```

---

## 💬 Sample AI Copilot Interactions

Try pasting these clinical scenarios into the assistant chat window:

```markdown
1. Log New Interaction:
"Visited Dr. Meera Iyer at City Hospital. Discussed Neurocalm efficacy and dosing; she was slightly hesitant regarding side effects. No samples given. Schedule a follow up for next Friday."

2. Multi-turn Correction:
"Actually, update that last meeting: the sentiment was positive and I provided 5 sample packs of Neurocalm."

3. Clinical History Query:
"What is my history with Dr. Adams and what was his sentiment during our previous visits?"

4. Pre-Call Preparation:
"Suggest talking points for my upcoming visit with Dr. Faizal regarding cardiology trials."
```

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

