"""
Claude API integration service.
"""
from anthropic import Anthropic
from typing import List, Dict
from ..config import settings

# Initialize Anthropic client
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def call_claude(system_prompt: str, user_message: str, max_tokens: int = 2000) -> str:
    """
    Call Claude API with a system prompt and user message.

    Args:
        system_prompt: System prompt for Claude
        user_message: User's message/question
        max_tokens: Maximum tokens in response

    Returns:
        Claude's response text
    """
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        # Extract text from response
        return response.content[0].text

    except Exception as e:
        print(f"Error calling Claude API: {e}")
        raise
