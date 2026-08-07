import threading
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from cachetools import TTLCache

from app.agent.schemas import TalkingPointsExtraction
from app.agent.tool_response import tool_envelope
from app.config import settings
from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction
from app.models.product import Product

# ── Module-level LLM (created once at startup, shared across all requests) ─────
_llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL_FALLBACK)
_structured_llm = _llm.with_structured_output(TalkingPointsExtraction)

# ── HCP history cache ──────────────────────────────────────────────────────────
# Interaction history for a given HCP rarely changes mid-session.
# Cache for 5 minutes to avoid repeated DB reads on every talking-points request.
_history_cache: TTLCache = TTLCache(maxsize=128, ttl=300)
_history_lock = threading.Lock()


@tool
def suggest_talking_points_tool(hcp_name: str, product_name: str | None = None) -> str:
    """
    Use this tool to get AI-suggested talking points for an upcoming visit with an HCP.
    Provide the HCP name and optionally a product name.
    When suggestions are generated, also pre-fills the Topics Discussed form field.
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

        # ── Cached HCP interaction history ─────────────────────────────────────
        cache_key = f"history:{target_hcp.id}"
        with _history_lock:
            cached_history = _history_cache.get(cache_key)

        if cached_history is not None:
            history_text = cached_history
        else:
            recent_interactions = (
                db.query(Interaction)
                .filter(Interaction.hcp_id == target_hcp.id)
                .order_by(Interaction.interaction_date.desc())
                .limit(5)
                .all()
            )

            history_text = "No past interactions."
            if recent_interactions:
                history_text = "\n".join(
                    [
                        f"- {ix.interaction_date}: Topics: {ix.topics_discussed}, "
                        f"Products: {ix.products_discussed}, Sentiment: {ix.sentiment}. "
                        f"Summary: {ix.summary}"
                        for ix in recent_interactions
                    ]
                )

            with _history_lock:
                _history_cache[cache_key] = history_text

        product_info = "No specific product mentioned."
        if product_name:
            product = (
                db.query(Product).filter(Product.name.ilike(f"%{product_name}%")).first()
            )
            if product:
                product_info = (
                    f"Focus on product '{product.name}' (Category: {product.category})."
                )
            else:
                product_info = (
                    f"Focus on product '{product_name}' (Note: Not found in database)."
                )

        prompt = (
            f"You are an AI assistant helping a pharmaceutical sales rep prepare for a meeting with Dr. {target_hcp.name}.\n"
            f"Specialty: {target_hcp.specialty}\n\n"
            f"Interaction History:\n{history_text}\n\n"
            f"Product Focus: {product_info}\n\n"
            "Generate 2-3 relevant, personalized, actionable talking points. "
            "Return them as short topic strings in topics_discussed and a friendly reply summarizing them."
        )

        try:
            extraction: TalkingPointsExtraction = _structured_llm.invoke(
                [HumanMessage(content=prompt)]
            )
        except Exception as e:
            return tool_envelope(
                f"Failed to generate talking points. Please try again. Error: {str(e)}",
                None,
            )

        form_data = {"topics_discussed": extraction.topics_discussed}
        return tool_envelope(extraction.reply, form_data)

    except Exception as e:
        return tool_envelope(f"An error occurred: {str(e)}", None)
    finally:
        db.close()
