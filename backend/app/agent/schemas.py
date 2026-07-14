from datetime import date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class InteractionExtraction(BaseModel):
    """
    Schema for extracting interaction details from a user's free-text input.
    """
    hcp_name: str = Field(description="The name of the Healthcare Professional (HCP). Example: 'Dr. Rao', 'Alice Smith'")
    interaction_date: date = Field(description="The date of the interaction. If not explicitly mentioned, assume today's date in YYYY-MM-DD format.")
    topics_discussed: List[str] = Field(default_factory=list, description="A list of topics discussed during the interaction.")
    products_discussed: List[str] = Field(default_factory=list, description="A list of products or medications discussed.")
    sentiment: str = Field(description="The sentiment of the interaction. Must be one of: positive, neutral, negative.")
    samples_given: Dict[str, Any] = Field(default_factory=dict, description="A dictionary of samples given, where the key is the product and the value is the quantity.")
    follow_up_required: bool = Field(default=False, description="True if a follow-up is required, False otherwise.")
    follow_up_date: Optional[date] = Field(default=None, description="The date the follow up should occur, if requested. YYYY-MM-DD format.")

class InteractionEditExtraction(BaseModel):
    """
    Schema for extracting updates to an existing interaction.
    All fields are optional; the LLM should only populate fields that the user explicitly requested to change.
    """
    interaction_date: Optional[date] = Field(default=None, description="The new date of the interaction in YYYY-MM-DD format.")
    topics_discussed: Optional[List[str]] = Field(default=None, description="The updated list of topics discussed.")
    products_discussed: Optional[List[str]] = Field(default=None, description="The updated list of products discussed.")
    sentiment: Optional[str] = Field(default=None, description="The updated sentiment: positive, neutral, or negative.")
    samples_given: Optional[Dict[str, Any]] = Field(default=None, description="The updated samples dictionary.")
    follow_up_required: Optional[bool] = Field(default=None, description="The updated follow-up requirement.")
    follow_up_date: Optional[date] = Field(default=None, description="The updated follow-up date.")
