import datetime
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_groq import ChatGroq

from app.agent.tool_response import tool_envelope
from app.config import settings
from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction
from app.models.follow_up import FollowUp


class DateExtraction(BaseModel):
    due_date: datetime.date = Field(description="The absolute date for the follow-up, parsed from the user's input based on today's date.")
    note: str = Field(description="A clean summary of what the follow-up entails.")


@tool
def schedule_follow_up_tool(hcp_name: str, follow_up_detail: str) -> str:
    """
    Use this tool to schedule a follow-up reminder for an HCP.
    Provide the name of the HCP and the details of the follow-up, including when it should happen (e.g., "in 2 weeks").
    """
    db = SessionLocal()
    try:
        # Find HCP
        search_term = f"%{hcp_name}%"
        matching_hcps = db.query(HCP).filter(HCP.name.ilike(search_term)).all()
        
        if len(matching_hcps) == 0:
            return tool_envelope(
                f"No HCP found matching '{hcp_name}'. Cannot schedule follow-up.",
                None,
            )
        if len(matching_hcps) > 1:
            names = ", ".join([hcp.name for hcp in matching_hcps])
            return tool_envelope(
                f"Found multiple HCPs matching '{hcp_name}': {names}. Please be more specific.",
                None,
            )

        target_hcp = matching_hcps[0]

        latest_interaction = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == target_hcp.id)
            .order_by(Interaction.interaction_date.desc())
            .first()
        )

        if not latest_interaction:
            return tool_envelope(
                f"No prior interactions found for {target_hcp.name}. "
                "A follow-up must be tied to an existing interaction.",
                None,
            )

        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)
        structured_llm = llm.with_structured_output(DateExtraction)

        today_str = datetime.date.today().strftime("%Y-%m-%d")
        prompt = (
            f"Today is {today_str}. The user said: '{follow_up_detail}'. "
            "Extract the absolute due date and a concise note."
        )

        try:
            extraction = structured_llm.invoke(prompt)
        except Exception as e:
            return tool_envelope(
                f"Failed to understand the date or details from the input. Error: {str(e)}",
                None,
            )

        new_follow_up = FollowUp(
            interaction_id=latest_interaction.id,
            due_date=extraction.due_date,
            status="pending",
            note=extraction.note,
        )
        db.add(new_follow_up)

        latest_interaction.follow_up_required = True
        latest_interaction.follow_up_date = extraction.due_date

        db.commit()

        form_data = {
            "follow_up_required": True,
            "follow_up_date": str(extraction.due_date),
        }
        return tool_envelope(
            f"Follow-up for {target_hcp.name} scheduled for {extraction.due_date}. "
            f"Note: {extraction.note}",
            form_data,
        )

    except Exception as e:
        db.rollback()
        return tool_envelope(f"An error occurred: {str(e)}", None)
    finally:
        db.close()
