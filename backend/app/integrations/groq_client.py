"""
integrations/groq_client.py — Centralised Groq LLM client factory.

Provides a single get_groq_client() factory so all agent tools share
the same configuration. Previously each tool instantiated ChatGroq directly.
"""
from langchain_groq import ChatGroq

from app.config import settings


def get_groq_client(temperature: float = 0) -> ChatGroq:
    """
    Return a configured ChatGroq instance.

    Args:
        temperature: Sampling temperature (0 = deterministic, default for tools).

    Returns:
        ChatGroq: Ready-to-use LLM client bound to the model from settings.
    """
    return ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=temperature,
    )
