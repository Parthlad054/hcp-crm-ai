from langchain_core.tools import tool
import json

from app.agent.tool_response import tool_envelope
from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction
from app.models.follow_up import FollowUp


@tool
def fetch_hcp_history_tool(hcp_name: str) -> str:
    """
    Use this tool to fetch the interaction history for a specific HCP.
    Provide the name of the HCP. Returns past interactions, last visit date, sentiment, and open follow-ups.
    When an HCP is resolved, also pre-fills the HCP name on the form.
    """
    db = SessionLocal()
    try:
        search_term = f"%{hcp_name}%"
        matching_hcps = db.query(HCP).filter(HCP.name.ilike(search_term)).all()

        if len(matching_hcps) == 0:
            return tool_envelope(f"No HCP found matching '{hcp_name}'.", None)
        if len(matching_hcps) > 1:
            names = ", ".join([hcp.name for hcp in matching_hcps])
            return tool_envelope(
                f"Found multiple HCPs matching '{hcp_name}': {names}. Please be more specific.",
                None,
            )

        target_hcp = matching_hcps[0]

        interactions = (
            db.query(Interaction)
            .filter(Interaction.hcp_id == target_hcp.id)
            .order_by(Interaction.interaction_date.desc())
            .all()
        )

        open_follow_ups = (
            db.query(FollowUp)
            .join(Interaction)
            .filter(Interaction.hcp_id == target_hcp.id, FollowUp.status == "pending")
            .all()
        )

        history = []
        sentiments = []
        for ix in interactions:
            history.append(
                {
                    "date": str(ix.interaction_date),
                    "summary": ix.summary or "No summary",
                    "topics": ix.topics_discussed,
                    "sentiment": ix.sentiment,
                }
            )
            if ix.sentiment:
                sentiments.append(ix.sentiment)

        follow_ups_data = [
            {"due_date": str(fu.due_date) if fu.due_date else None, "note": fu.note}
            for fu in open_follow_ups
        ]

        last_visit_date = (
            str(target_hcp.last_interaction_date)
            if target_hcp.last_interaction_date
            else "Never"
        )

        form_data = {"hcp_name": target_hcp.name}
        
        reply_lines = [f"### History for **{target_hcp.name}**"]
        reply_lines.append(f"**Specialty**: {target_hcp.specialty or 'N/A'}")
        reply_lines.append(f"**Last Visit**: {last_visit_date}")
        
        if sentiments:
            reply_lines.append(f"**Recent Sentiment Trend**: {', '.join(sentiments[:5])}")
            
        if follow_ups_data:
            reply_lines.append("\n**Open Follow-ups**:")
            for fu in follow_ups_data:
                date_str = fu.get('due_date') or 'No date'
                reply_lines.append(f"- {date_str}: {fu.get('note')}")
                
        if history:
            reply_lines.append("\n**Recent Interactions**:")
            for ix in history[:5]:
                topics = ix.get('topics')
                topics_str = ", ".join(topics) if topics else "None"
                sentiment_str = ix.get('sentiment') or 'neutral'
                reply_lines.append(f"- **{ix.get('date')}** ({sentiment_str}): {ix.get('summary')} (Topics: {topics_str})")
        else:
            reply_lines.append("\n*No previous interactions recorded.*")

        reply = "\n".join(reply_lines)

        return tool_envelope(reply, form_data)

    except Exception as e:
        return tool_envelope(f"An error occurred: {str(e)}", None)
    finally:
        db.close()
