import datetime
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from app.agent.schemas import InteractionExtraction
from app.config import settings
from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction


@tool
def log_interaction_tool(text: str) -> str:
    """
    Use this tool to log a new interaction with an HCP.
    Provide the raw free text containing details about the interaction (like doctor's name, topics, sentiment).
    """
    # 1. Initialize LLM
    llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)
    
    # 2. Extract structured data
    structured_llm = llm.with_structured_output(InteractionExtraction)
    
    # We provide the current date in the prompt so the LLM knows what "today" means
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    prompt = f"Today is {today_str}. Extract the interaction details from the following text:\n\n{text}"
    
    try:
        extracted: InteractionExtraction = structured_llm.invoke(prompt)
    except Exception as e:
        return f"Failed to extract interaction details. Please provide more clear information. Error: {str(e)}"
    
    # 3. Query the DB for the HCP
    db = SessionLocal()
    try:
        # Simple fuzzy match using ILIKE
        search_term = f"%{extracted.hcp_name}%"
        matching_hcps = db.query(HCP).filter(HCP.name.ilike(search_term)).all()
        
        if len(matching_hcps) == 0:
            return f"I couldn't find an HCP matching '{extracted.hcp_name}' in the system. Could you clarify the name?"
        elif len(matching_hcps) > 1:
            names = ", ".join([hcp.name for hcp in matching_hcps])
            return f"I found multiple HCPs matching '{extracted.hcp_name}': {names}. Which one did you mean?"
        
        target_hcp = matching_hcps[0]
        
        # 4. Generate a short summary
        summary_prompt = f"Summarize this interaction in 1-2 sentences: {text}"
        summary_response = llm.invoke([HumanMessage(content=summary_prompt)])
        summary_text = summary_response.content
        
        # 5. Insert into the DB
        new_interaction = Interaction(
            hcp_id=target_hcp.id,
            rep_id="demo_rep",  # Hardcoded for Phase 1 as auth is out of scope
            interaction_date=extracted.interaction_date,
            channel="in-person",  # Defaulting to in-person for chat, could also be extracted
            topics_discussed=extracted.topics_discussed,
            products_discussed=extracted.products_discussed,
            sentiment=extracted.sentiment,
            samples_given=extracted.samples_given,
            follow_up_required=extracted.follow_up_required,
            follow_up_date=extracted.follow_up_date,
            raw_input=text,
            summary=summary_text,
            source="chat"
        )
        db.add(new_interaction)
        
        # Also update the HCP's last_interaction_date
        if not target_hcp.last_interaction_date or target_hcp.last_interaction_date < extracted.interaction_date:
            target_hcp.last_interaction_date = extracted.interaction_date
            
        db.commit()
        
        return f"Successfully logged interaction with {target_hcp.name} on {extracted.interaction_date}. Summary: {summary_text}"
        
    except Exception as e:
        db.rollback()
        return f"An error occurred while saving the interaction: {str(e)}"
    finally:
        db.close()
