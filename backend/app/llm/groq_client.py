"""
Groq LLM client — shared across all agent tools.
Run this file directly as a smoke test:
    python -m app.llm.groq_client
"""
import os

from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def chat_completion(messages: list[dict], model: str | None = None) -> str:
    """Send a list of messages to Groq and return the assistant's text reply."""
    model = model or settings.GROQ_MODEL
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content


def test_connection() -> None:
    reply = chat_completion(
        messages=[{"role": "user", "content": "Reply with OK if you can read this."}]
    )
    print(f"[Groq smoke test] Model: {settings.GROQ_MODEL} | Response: {reply}")


if __name__ == "__main__":
    test_connection()
