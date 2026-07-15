from typing import Annotated, Any, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Shared state for the LangGraph agent.
    - messages: Conversation history and tool invocations.
    - session_id: Optional chat session identifier.
    - current_form_state: Draft form from the left panel (for selective edits).
    - form_data: Structured fields to merge into the left panel (or null).
    - reply: Final assistant reply string surfaced by /chat.
    """
    messages: Annotated[list[AnyMessage], add_messages]
    session_id: str | None
    current_form_state: dict[str, Any] | None
    form_data: dict[str, Any] | None
    reply: str | None
