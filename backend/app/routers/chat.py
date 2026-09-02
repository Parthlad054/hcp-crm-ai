import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage

from app.agent.graph import graph
from app.auth.security import get_current_user
from app.config import settings
from app.limiter import limiter
from app.models.user import User

from app.schemas.common import ApiResponse

logger = logging.getLogger(__name__)

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


@router.post("/", response_model=ApiResponse[ChatResponse])
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
    try:
        final_state = await asyncio.to_thread(graph.invoke, state)
    except Exception as exc:
        logger.error("Error during LangGraph agent execution: %s", exc, exc_info=True)
        err_msg = str(exc)
        if "model_not_found" in err_msg or "NotFoundError" in type(exc).__name__:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq model error: The configured model '{settings.GROQ_MODEL}' was not found or is unavailable. Please verify GROQ_MODEL in your .env file.",
            )
        elif "authentication" in err_msg.lower() or "AuthenticationError" in type(exc).__name__:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Groq authentication failed. Please verify GROQ_API_KEY in your .env file.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI Agent error: {err_msg}",
        )

    reply = final_state.get("reply")
    if not reply:
        final_message = final_state["messages"][-1]
        reply = getattr(final_message, "content", "") or ""

    return ApiResponse(
        statusCode=200,
        message="Chat response generated successfully",
        data=ChatResponse(
            reply=reply,
            form_data=final_state.get("form_data"),
            session_id=payload.session_id,
        ),
    )
