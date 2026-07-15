import json
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.agent.form_context import get_current_form_state
from app.agent.schemas import InteractionEditExtraction
from app.agent.tool_response import (
    baseline_form_state,
    format_edit_reply,
    merge_form_patch,
    tool_envelope,
)
from app.config import settings
from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction

EDIT_SYSTEM_PROMPT = (
    "Given the CURRENT_FORM (JSON) and a USER_CORRECTION (text), return a JSON object "
    "containing ONLY the fields that need to change based on the correction. "
    "Do not include fields that are not mentioned or implied by the correction. "
    "Do not guess values for unrelated fields. "
    "Leave every other field unset."
)


def _patch_to_form_fields(patch: InteractionEditExtraction) -> dict:
    """Convert optional edit extraction into form_data keys (only explicitly set fields)."""
    raw = patch.model_dump(exclude_unset=True)
    out: dict = {}
    if "hcp_name" in raw and raw["hcp_name"] is not None:
        out["hcp_name"] = raw["hcp_name"]
    if "interaction_date" in raw and raw["interaction_date"] is not None:
        out["date"] = str(raw["interaction_date"])
    if "channel" in raw and raw["channel"] is not None:
        out["channel"] = raw["channel"]
    if "topics_discussed" in raw and raw["topics_discussed"] is not None:
        out["topics_discussed"] = raw["topics_discussed"]
    if "products_discussed" in raw and raw["products_discussed"] is not None:
        out["products_discussed"] = raw["products_discussed"]
    if "sentiment" in raw and raw["sentiment"] is not None:
        out["sentiment"] = raw["sentiment"]
    if "samples_given" in raw and raw["samples_given"] is not None:
        out["samples_given"] = raw["samples_given"]
    if "follow_up_required" in raw and raw["follow_up_required"] is not None:
        out["follow_up_required"] = raw["follow_up_required"]
    if "follow_up_date" in raw:
        out["follow_up_date"] = (
            str(raw["follow_up_date"]) if raw["follow_up_date"] is not None else None
        )
    return out


def _apply_db_patch(interaction: Interaction, patch: InteractionEditExtraction) -> dict:
    """Apply the same selective patch to a saved DB row — never full-row replacement."""
    db_fields = patch.model_dump(exclude_unset=True)
    changes_made: dict = {}

    for field, new_value in db_fields.items():
        if field == "hcp_name":
            continue
        if field == "channel" and new_value is not None:
            old_value = interaction.channel
            if old_value != new_value:
                interaction.channel = new_value
                changes_made[field] = {"old": old_value, "new": new_value}
            continue
        if new_value is None:
            continue
        old_value = getattr(interaction, field, None)
        if old_value != new_value:
            setattr(interaction, field, new_value)
            changes_made[field] = {"old": old_value, "new": new_value}

    return changes_made


@tool
def edit_interaction_tool(change_request: str, reference: str = "") -> str:
    """
    Use this tool to SELECTIVELY edit fields on the current in-progress form.
    Call when the user corrects specific fields (e.g. "change the name to Dr. John", "sentiment was negative").
    Uses current_form_state from the left panel as the baseline — only changed fields are patched.
    Provide the change request in natural language.
    Optionally provide a reference (interaction ID or HCP name) to also patch a saved DB record.
    """
    current_form = baseline_form_state(get_current_form_state())

    if not current_form:
        return tool_envelope(
            "There is no form data to edit yet. Describe an interaction first so I can fill the form.",
            None,
        )

    llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL)
    structured_llm = llm.with_structured_output(InteractionEditExtraction)

    user_prompt = (
        f"CURRENT_FORM:\n{json.dumps(current_form, indent=2, default=str)}\n\n"
        f"USER_CORRECTION:\n{change_request}"
    )

    try:
        patch: InteractionEditExtraction = structured_llm.invoke(
            [
                SystemMessage(content=EDIT_SYSTEM_PROMPT),
                HumanMessage(content=user_prompt),
            ]
        )
    except Exception as e:
        return tool_envelope(
            f"Failed to understand the requested edits. Error: {str(e)}",
            None,
        )

    form_patch = _patch_to_form_fields(patch)
    if not form_patch:
        return tool_envelope(
            "I couldn't identify any specific fields to change. Please say which field to update.",
            None,
        )

    merged_form = merge_form_patch(current_form, form_patch)
    reply = format_edit_reply(current_form, form_patch)

    # Only sync to DB when caller explicitly passes a reference (post-save editing)
    ref = (reference or "").strip()
    if ref:
        db = SessionLocal()
        try:
            interaction_to_edit = None

            if ref.isdigit():
                interaction_to_edit = (
                    db.query(Interaction).filter(Interaction.id == int(ref)).first()
                )
            else:
                search_term = f"%{ref}%"
                matching_hcps = db.query(HCP).filter(HCP.name.ilike(search_term)).all()
                if len(matching_hcps) == 1:
                    target_hcp = matching_hcps[0]
                    interaction_to_edit = (
                        db.query(Interaction)
                        .filter(Interaction.hcp_id == target_hcp.id)
                        .order_by(
                            Interaction.interaction_date.desc(),
                            Interaction.created_at.desc(),
                        )
                        .first()
                    )

            if interaction_to_edit:
                changes_made = _apply_db_patch(interaction_to_edit, patch)
                if changes_made:
                    new_data_str = json.dumps(
                        {
                            "interaction_date": str(interaction_to_edit.interaction_date),
                            "topics": interaction_to_edit.topics_discussed,
                            "products": interaction_to_edit.products_discussed,
                            "sentiment": interaction_to_edit.sentiment,
                            "samples": interaction_to_edit.samples_given,
                            "raw_input": interaction_to_edit.raw_input,
                        },
                        default=str,
                    )
                    summary_prompt = (
                        f"Summarize this updated interaction in 1-2 sentences: {new_data_str}"
                    )
                    summary_response = llm.invoke([HumanMessage(content=summary_prompt)])
                    interaction_to_edit.summary = summary_response.content
                    merged_form["summary"] = summary_response.content
                    db.commit()
                    reply += f" Saved interaction (ID: {interaction_to_edit.id}) was patched with the same changes."
                else:
                    reply += " No saved interaction fields needed updating."
            else:
                reply += " Could not find a saved interaction for that reference."
        except Exception as e:
            db.rollback()
            reply += f" (Saved record update skipped: {str(e)})"
        finally:
            db.close()

    return tool_envelope(reply, merged_form)
