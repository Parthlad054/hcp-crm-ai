from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.agent.form_context import reset_current_form_state, set_current_form_state
from app.agent.state import AgentState
from app.agent.tool_response import parse_tool_envelope
from app.config import settings
from app.agent.tools.log_interaction import log_interaction_tool
from app.agent.tools.edit_interaction import edit_interaction_tool
from app.agent.tools.fetch_hcp_history import fetch_hcp_history_tool
from app.agent.tools.schedule_follow_up import schedule_follow_up_tool
from app.agent.tools.suggest_talking_points import suggest_talking_points_tool

llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)

tools = [
    log_interaction_tool,
    edit_interaction_tool,
    fetch_hcp_history_tool,
    schedule_follow_up_tool,
    suggest_talking_points_tool,
]

llm_with_tools = llm.bind_tools(tools)
_base_tool_node = ToolNode(tools)

SYSTEM_ROUTER_PROMPT = """You are an AI CRM assistant that controls a structured interaction form on the left panel.

Routing rules:
- log_interaction: user describes a NEW visit/call (names, topics, products, sentiment). Fills the form.
- edit_interaction: user wants to CORRECT specific fields on the current form (e.g. "change name to Dr. John", "sentiment was negative"). Only touch requested fields.
- fetch_hcp_history: user asks for past interactions / history.
- schedule_follow_up: user wants to schedule a follow-up reminder.
- suggest_talking_points: user wants talking points for an upcoming visit.

Prefer a tool call when the request matches one of the above. Do not invent tools.
"""


def router(state: AgentState) -> dict:
    """Router Node: Calls the LLM to determine intent and optionally emit tool calls."""
    messages = list(state["messages"])
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_ROUTER_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", "response"]:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "response"


def tools_node(state: AgentState) -> dict:
    """
    Wrap ToolNode so edit_interaction can read current_form_state via ContextVar,
    then lift reply/form_data from tool envelopes into graph state.
    """
    token = set_current_form_state(state.get("current_form_state"))
    try:
        result = _base_tool_node.invoke(state)
    finally:
        reset_current_form_state(token)

    form_data = None
    reply = None
    for msg in result.get("messages", []):
        if getattr(msg, "type", None) == "tool":
            parsed_reply, parsed_form = parse_tool_envelope(msg.content)
            reply = parsed_reply
            if parsed_form is not None:
                form_data = parsed_form

    out = {"messages": result.get("messages", [])}
    if form_data is not None:
        out["form_data"] = form_data
    if reply is not None:
        out["reply"] = reply
    return out


def response_formatter(state: AgentState) -> dict:
    """
    Response Node: Prefer structured tool reply; otherwise use the last AI message.
    Surfaces reply + form_data for the /chat endpoint.
    """
    last_message = state["messages"][-1]
    form_data = state.get("form_data")
    reply = state.get("reply")

    if last_message.type == "tool":
        tool_reply, tool_form = parse_tool_envelope(last_message.content)
        if tool_form is not None:
            form_data = tool_form
        reply = tool_reply or reply
        return {
            "messages": [AIMessage(content=reply or "")],
            "form_data": form_data,
            "reply": reply,
        }

    # No tool was used — last message is the router's AI reply
    content = getattr(last_message, "content", "") or ""
    return {
        "messages": [],
        "form_data": form_data,
        "reply": content,
    }


workflow = StateGraph(AgentState)

workflow.add_node("router", router)
workflow.add_node("tools", tools_node)
workflow.add_node("response", response_formatter)

workflow.add_edge(START, "router")
workflow.add_conditional_edges("router", should_continue)
workflow.add_edge("tools", "response")
workflow.add_edge("response", END)

graph = workflow.compile()
