from typing import Literal
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from app.agent.state import AgentState
from app.config import settings
from app.agent.tools.log_interaction import log_interaction_tool
from app.agent.tools.edit_interaction import edit_interaction_tool
from app.agent.tools.stubs import (
    fetch_hcp_history_tool,
    schedule_follow_up_tool,
    suggest_talking_points_tool,
)

# Initialize the LLM with the primary model
llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)

# Define the tools available to the agent
tools = [
    log_interaction_tool,
    edit_interaction_tool,
    fetch_hcp_history_tool,
    schedule_follow_up_tool,
    suggest_talking_points_tool,
]

# Bind the tools to the LLM
llm_with_tools = llm.bind_tools(tools)

# The ToolNode automatically executes the tools when requested by the LLM
tool_node = ToolNode(tools)

def router(state: AgentState) -> dict:
    """
    Router Node: Calls the LLM to determine the user's intent.
    If the LLM decides to call a tool, it outputs a tool call.
    """
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", "response"]:
    """
    Conditional edge: Determines whether to execute a tool or proceed to formatting the response.
    """
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "response"

def response_formatter(state: AgentState) -> dict:
    """
    Response Node: Formats the final output back to the user after a tool has been executed
    or if no tool was needed. We pass the conversation so the LLM can summarize the result.
    """
    # If the last message was a tool message, we ask the LLM to summarize the result
    last_message = state["messages"][-1]
    
    # We use the fallback model for final synthesis or just the same model. 
    # Here we'll use the main model for simplicity.
    synthesis_llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)
    
    # If it's a tool response, we instruct the LLM to provide a final answer
    if last_message.type == "tool":
        # System prompt can be added temporarily to guide the summarization
        # For simplicity, we just invoke it with the history
        response = synthesis_llm.invoke(state["messages"])
        return {"messages": [response]}
        
    return {"messages": []}

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("router", router)
workflow.add_node("tools", tool_node)
workflow.add_node("response", response_formatter)

# Define edges
workflow.add_edge(START, "router")
workflow.add_conditional_edges("router", should_continue)
workflow.add_edge("tools", "response")
workflow.add_edge("response", END)

# Compile the graph
graph = workflow.compile()
