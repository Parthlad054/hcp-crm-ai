from langchain_core.tools import tool


@tool
def fetch_hcp_history_tool(hcp_name: str) -> str:
    """
    Use this tool to fetch the interaction history for a specific HCP.
    Provide the name of the HCP.
    """
    return f"[Stub] Retrieved history for {hcp_name}."

@tool
def schedule_follow_up_tool(follow_up_detail: str) -> str:
    """
    Use this tool to schedule a follow-up reminder for an HCP.
    Provide the details of the follow-up, including dates and notes.
    """
    return "[Stub] Follow-up scheduled successfully."

@tool
def suggest_talking_points_tool(hcp_name: str, product_name: str | None = None) -> str:
    """
    Use this tool to get AI-suggested talking points for an upcoming visit with an HCP.
    Provide the HCP name and optionally a product name.
    """
    return f"[Stub] Suggested talking points for {hcp_name} generated."
