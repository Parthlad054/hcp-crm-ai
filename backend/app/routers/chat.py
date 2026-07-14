from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str | None = None


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatMessage):
    """
    Route a free-text message through the LangGraph agent.
    Agent logic is wired in Phase 2 — this is a stub that confirms the endpoint is reachable.
    """
    # TODO (Phase 2): replace stub with LangGraph agent invocation
    return ChatResponse(
        reply="[Agent stub] Message received. LangGraph agent wired in Phase 2.",
        session_id=payload.session_id,
    )
