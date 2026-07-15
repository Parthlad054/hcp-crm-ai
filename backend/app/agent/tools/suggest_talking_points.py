from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from app.config import settings
from app.database import SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction
from app.models.product import Product


@tool
def suggest_talking_points_tool(hcp_name: str, product_name: str | None = None) -> str:
    """
    Use this tool to get AI-suggested talking points for an upcoming visit with an HCP.
    Provide the HCP name and optionally a product name.
    """
    db = SessionLocal()
    try:
        # 1. Find HCP
        search_term = f"%{hcp_name}%"
        matching_hcps = db.query(HCP).filter(HCP.name.ilike(search_term)).all()
        
        if len(matching_hcps) == 0:
            return f"No HCP found matching '{hcp_name}'."
        elif len(matching_hcps) > 1:
            names = ", ".join([hcp.name for hcp in matching_hcps])
            return f"Found multiple HCPs matching '{hcp_name}': {names}. Please be more specific."
            
        target_hcp = matching_hcps[0]
        
        # 2. Get interaction history (last 5)
        recent_interactions = db.query(Interaction).filter(
            Interaction.hcp_id == target_hcp.id
        ).order_by(Interaction.interaction_date.desc()).limit(5).all()
        
        history_text = "No past interactions."
        if recent_interactions:
            history_text = "\n".join([
                f"- {ix.interaction_date}: Topics: {ix.topics_discussed}, Products: {ix.products_discussed}, Sentiment: {ix.sentiment}. Summary: {ix.summary}"
                for ix in recent_interactions
            ])
            
        # 3. Get product info if provided
        product_info = "No specific product mentioned."
        if product_name:
            product = db.query(Product).filter(Product.name.ilike(f"%{product_name}%")).first()
            if product:
                product_info = f"Focus on product '{product.name}' (Category: {product.category})."
            else:
                product_info = f"Focus on product '{product_name}' (Note: Not found in database)."
                
        # 4. Call LLM (using fallback/larger model per requirements)
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=settings.GROQ_MODEL_FALLBACK)
        
        prompt = (
            f"You are an AI assistant helping a pharmaceutical sales rep prepare for a meeting with Dr. {target_hcp.name}.\n"
            f"Specialty: {target_hcp.specialty}\n\n"
            f"Interaction History:\n{history_text}\n\n"
            f"Product Focus: {product_info}\n\n"
            "Based on this history and focus, generate 2-3 relevant, personalized, and actionable talking points for the next visit."
        )
        
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
        
    except Exception as e:
        return f"An error occurred: {str(e)}"
    finally:
        db.close()
