from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str | None = None


from app.agent.graph import graph
from langchain_core.messages import HumanMessage

@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatMessage):
    """
    Route a free-text message through the LangGraph agent.
    """
    input_message = HumanMessage(content=payload.message)
    state = {"messages": [input_message], "session_id": payload.session_id}
    
    # Invoke the graph synchronously (since we're keeping it simple as per plan)
    final_state = graph.invoke(state)
    
    # The final message in the state should be the AI's response
    final_message = final_state["messages"][-1]
    
    return ChatResponse(
        reply=final_message.content,
        session_id=payload.session_id,
    )
