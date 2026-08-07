import asyncio
from typing import Any

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from app.agent.graph import graph
from app.auth.security import get_current_user
from app.limiter import limiter
from app.models.user import User

router = APIRouter()


class FormState(BaseModel):
    hcp_name: str | None = None
    date: str | None = None
    interaction_date: str | None = None  # accepted alias from frontend
    channel: str | None = None
    products_discussed: list | str | None = None
    topics_discussed: list | str | None = None
    sentiment: str | None = None
    samples_given: dict | None = None
    follow_up_required: bool | None = None
    follow_up_date: str | None = None
    summary: str | None = None


class ChatMessage(BaseModel):
    message: str
    current_form_state: FormState | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    form_data: dict[str, Any] | None = Field(
        default=None,
        description="Full or partial form object to merge into the left panel, or null.",
    )
    session_id: str | None = None


@router.post("/", response_model=ChatResponse)
@limiter.limit("30/minute")
async def chat(
    request: Request,
    payload: ChatMessage,
    current_user: User = Depends(get_current_user),
):
    """
    Route a free-text message through the LangGraph agent.
    Passes current_form_state for selective edits; returns form_data for the UI.
    Requires authentication. Rate-limited: 30 messages per IP per minute.
    """
    form_state = None
    if payload.current_form_state is not None:
        form_state = payload.current_form_state.model_dump(exclude_none=False)

    input_message = HumanMessage(content=payload.message)
    state = {
        "messages": [input_message],
        "session_id": payload.session_id,
        "current_form_state": form_state,
        "form_data": None,
        "reply": None,
        "rep_id": current_user.email,
    }

    # graph.invoke is synchronous (LangGraph); run in a thread pool so we
    # never block the uvicorn async event loop for other concurrent requests.
    final_state = await asyncio.to_thread(graph.invoke, state)

    reply = final_state.get("reply")
    if not reply:
        final_message = final_state["messages"][-1]
        reply = getattr(final_message, "content", "") or ""

    return ChatResponse(
        reply=reply,
        form_data=final_state.get("form_data"),
        session_id=payload.session_id,
    )
