import datetime
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from app.agent.schemas import InteractionExtraction
from app.agent.tool_response import extracted_to_form_data, tool_envelope
from app.config import settings
from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction


@tool
def log_interaction_tool(text: str) -> str:
    """
    Use this tool to log a NEW interaction and fill the left-panel form from free text.
    Call when the user describes a visit/call (HCP name, topics, products, sentiment, etc.).
    Provide the raw free text containing details about the interaction.
    Returns a reply plus structured form_data for the UI.
    """
    llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)
    structured_llm = llm.with_structured_output(InteractionExtraction)

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    prompt = f"Today is {today_str}. Extract the interaction details from the following text:\n\n{text}"

    try:
        extracted: InteractionExtraction = structured_llm.invoke(prompt)
    except Exception as e:
        return tool_envelope(
            f"Failed to extract interaction details. Please provide clearer information. Error: {str(e)}",
            None,
        )

    # Generate a short summary for both DB and form
    summary_prompt = f"Summarize this interaction in 1-2 sentences: {text}"
    summary_response = llm.invoke([HumanMessage(content=summary_prompt)])
    summary_text = summary_response.content

    channel = extracted.channel if extracted.channel else "in-person"
    form_data = extracted_to_form_data(extracted, channel=channel, summary=summary_text)

    db = SessionLocal()
    try:
        search_term = f"%{extracted.hcp_name}%"
        matching_hcps = db.query(HCP).filter(HCP.name.ilike(search_term)).all()

        if len(matching_hcps) == 0:
            return tool_envelope(
                f"I've filled the form with details for '{extracted.hcp_name}'. "
                "That HCP is not in the system yet — review the form and click Log Interaction to create them and save.",
                form_data,
            )
        if len(matching_hcps) > 1:
            names = ", ".join([hcp.name for hcp in matching_hcps])
            return tool_envelope(
                f"I've pre-filled the form. Multiple HCPs match '{extracted.hcp_name}': {names}. "
                "Please confirm the correct name on the form before saving.",
                form_data,
            )

        target_hcp = matching_hcps[0]
        form_data["hcp_name"] = target_hcp.name

        new_interaction = Interaction(
            hcp_id=target_hcp.id,
            rep_id="demo_rep",
            interaction_date=extracted.interaction_date,
            channel=channel,
            topics_discussed=extracted.topics_discussed,
            products_discussed=extracted.products_discussed,
            sentiment=extracted.sentiment,
            samples_given=extracted.samples_given,
            follow_up_required=extracted.follow_up_required,
            follow_up_date=extracted.follow_up_date,
            raw_input=text,
            summary=summary_text,
            source="chat",
        )
        db.add(new_interaction)

        if (
            not target_hcp.last_interaction_date
            or target_hcp.last_interaction_date < extracted.interaction_date
        ):
            target_hcp.last_interaction_date = extracted.interaction_date

        db.commit()

        return tool_envelope(
            f"Form filled and interaction logged with {target_hcp.name} on {extracted.interaction_date}. "
            f"Summary: {summary_text}",
            form_data,
        )

    except Exception as e:
        db.rollback()
        # Still return form_data so the left panel can update even if DB write fails
        return tool_envelope(
            f"Form filled, but saving to the database failed: {str(e)}. "
            "You can still review the form and click Log Interaction.",
            form_data,
        )
    finally:
        db.close()
