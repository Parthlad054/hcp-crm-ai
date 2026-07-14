from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Shared state for the LangGraph agent.
    - messages: Tracks the conversation history and tool invocations.
    - session_id: Optional tracking identifier for the current chat session.
    """
    messages: Annotated[list[AnyMessage], add_messages]
    session_id: str | None
