from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import interactions, chat, hcps, follow_ups

app = FastAPI(
    title="AI-First CRM — HCP Module",
    description="LangGraph-powered CRM backend for field reps logging HCP interactions.",
    version="0.1.0",
)

# Allow the React dev server (and any origin in dev) to reach the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(hcps.router, prefix="/hcps", tags=["hcps"])
app.include_router(follow_ups.router, prefix="/follow-ups", tags=["follow-ups"])


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
