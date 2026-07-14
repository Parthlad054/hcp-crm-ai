import json
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from app.agent.schemas import InteractionEditExtraction
from app.config import settings
from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction


@tool
def edit_interaction_tool(reference: str, change_request: str) -> str:
    """
    Use this tool to edit an existing interaction with an HCP.
    Provide a reference (like 'my last log with Dr. X' or an interaction ID) and the requested changes in natural language.
    """
    db = SessionLocal()
    try:
        interaction_to_edit = None
        
        # Determine if reference is likely an ID or a name
        if reference.strip().isdigit():
            interaction_to_edit = db.query(Interaction).filter(Interaction.id == int(reference)).first()
        else:
            # Fuzzy match HCP and get their latest interaction
            search_term = f"%{reference.strip()}%"
            matching_hcps = db.query(HCP).filter(HCP.name.ilike(search_term)).all()
            
            if len(matching_hcps) == 0:
                return f"I couldn't find an HCP matching '{reference}'. Please clarify."
            elif len(matching_hcps) > 1:
                names = ", ".join([hcp.name for hcp in matching_hcps])
                return f"I found multiple HCPs matching '{reference}': {names}. Which one did you mean?"
                
            target_hcp = matching_hcps[0]
            
            # Fetch the most recent interaction for this HCP
            interaction_to_edit = db.query(Interaction).filter(
                Interaction.hcp_id == target_hcp.id
            ).order_by(Interaction.interaction_date.desc(), Interaction.created_at.desc()).first()
            
        if not interaction_to_edit:
            return "Could not find an interaction matching that reference to edit."

        # Serialize current state for the LLM
        current_data = {
            "interaction_date": str(interaction_to_edit.interaction_date) if interaction_to_edit.interaction_date else None,
            "topics_discussed": interaction_to_edit.topics_discussed,
            "products_discussed": interaction_to_edit.products_discussed,
            "sentiment": interaction_to_edit.sentiment,
            "samples_given": interaction_to_edit.samples_given,
            "follow_up_required": interaction_to_edit.follow_up_required,
            "follow_up_date": str(interaction_to_edit.follow_up_date) if interaction_to_edit.follow_up_date else None,
            "summary": interaction_to_edit.summary,
        }
        
        # 1. Initialize LLM
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)
        
        # 2. Extract structured patch
        structured_llm = llm.with_structured_output(InteractionEditExtraction)
        prompt = f"Current Interaction Data:\n{json.dumps(current_data, indent=2)}\n\nChange Request: {change_request}\n\nReturn the fields that need to be updated."
        
        try:
            patch: InteractionEditExtraction = structured_llm.invoke(prompt)
        except Exception as e:
            return f"Failed to understand the requested edits. Error: {str(e)}"
            
        # 3. Apply the patch dynamically
        changes_made = {}
        for field, new_value in patch.model_dump(exclude_unset=True, exclude_none=True).items():
            old_value = getattr(interaction_to_edit, field)
            if old_value != new_value:
                setattr(interaction_to_edit, field, new_value)
                changes_made[field] = {"old": old_value, "new": new_value}
                
        if not changes_made:
            return "I couldn't identify any changes to make based on your request."
            
        # 4. Generate new summary
        new_data_str = json.dumps({
            "interaction_date": str(interaction_to_edit.interaction_date),
            "topics": interaction_to_edit.topics_discussed,
            "products": interaction_to_edit.products_discussed,
            "sentiment": interaction_to_edit.sentiment,
            "samples": interaction_to_edit.samples_given,
            "raw_input": interaction_to_edit.raw_input
        })
        summary_prompt = f"Summarize this updated interaction in 1-2 sentences: {new_data_str}"
        summary_response = llm.invoke([HumanMessage(content=summary_prompt)])
        interaction_to_edit.summary = summary_response.content
        
        db.commit()
        
        # Format the before/after response
        changes_str = "\n".join([f"- **{k}**: {v['old']} -> {v['new']}" for k, v in changes_made.items()])
        return f"Updated interaction (ID: {interaction_to_edit.id}). Changes made:\n{changes_str}\n\nNew Summary: {interaction_to_edit.summary}"
        
    except Exception as e:
        db.rollback()
        return f"An error occurred while editing the interaction: {str(e)}"
    finally:
        db.close()
