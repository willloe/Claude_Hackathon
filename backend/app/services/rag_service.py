"""
RAG (Retrieval Augmented Generation) service orchestration.
"""
from typing import List, Dict, Optional
from .vector_store import vector_store
from .claude_service import call_claude
from .. import models


PERSONA_DESCRIPTIONS = {
    "policy_first": "strict and policy-focused, always checking rules before answering",
    "friendly": "warm and encouraging, balancing helpfulness with academic integrity",
    "scaffolded": "Socratic and guiding, asking questions to help students think through problems"
}


def build_system_prompt(
    course_name: str,
    term: str,
    policy: Optional[models.CoursePolicy],
    context_chunks: List[Dict[str, any]]
) -> str:
    """
    Build the system prompt for Claude.

    Args:
        course_name: Course name
        term: Course term
        policy: Course policy configuration
        context_chunks: Retrieved context chunks

    Returns:
        System prompt string
    """
    # Get persona description
    persona = "friendly"
    allowed_topics = "All course-related topics"
    disallowed_actions = "Do not provide complete solutions to assignments or exam answers"
    custom_instructions = ""

    if policy:
        persona = policy.persona.value
        if policy.allowed_topics:
            allowed_topics = policy.allowed_topics
        if policy.disallowed_actions:
            disallowed_actions = policy.disallowed_actions
        if policy.custom_instructions:
            custom_instructions = f"\n\nADDITIONAL INSTRUCTIONS:\n{policy.custom_instructions}"

    persona_desc = PERSONA_DESCRIPTIONS.get(persona, PERSONA_DESCRIPTIONS["friendly"])

    # Format context chunks
    context_text = ""
    if context_chunks:
        context_text = "\n\nRETRIEVED CONTEXT:\n"
        for i, chunk in enumerate(context_chunks, 1):
            filename = chunk['metadata'].get('filename', 'Unknown')
            page = chunk['metadata'].get('page', '?')
            text = chunk['text']
            context_text += f"\n[Source {i}: {filename}, page {page}]\n{text}\n"
    else:
        context_text = "\n\nRETRIEVED CONTEXT:\nNo relevant context found in course materials."

    system_prompt = f"""You are an AI Teaching Assistant for {course_name} ({term}).

COURSE POLICIES:
- Persona: {persona_desc}
- Allowed topics: {allowed_topics}
- Disallowed actions: {disallowed_actions}{custom_instructions}

STRICT RULES:
1. Always cite sources using the format [Source: filename, page X] when using information from the context
2. If asked for disallowed content (like complete assignment solutions or exam answers), politely refuse and suggest alternatives like:
   - Explaining concepts
   - Providing similar examples
   - Guiding through problem-solving steps
3. If the information needed to answer isn't in the provided context, say so honestly
4. Keep answers focused and educational
5. When refusing a request, start your response with "I cannot provide that because..."

{context_text}

Answer the student's question using ONLY the provided context. Always cite your sources when referencing specific information."""

    return system_prompt


def detect_refusal(answer: str) -> bool:
    """
    Detect if the answer contains a refusal.

    Args:
        answer: Claude's answer

    Returns:
        True if answer contains refusal, False otherwise
    """
    refusal_phrases = [
        "I cannot provide",
        "I can't provide",
        "I'm not able to",
        "I cannot help with",
        "I can't help with",
        "would violate",
        "not appropriate",
        "against the policy"
    ]

    answer_lower = answer.lower()
    return any(phrase.lower() in answer_lower for phrase in refusal_phrases)


async def answer_question(
    course_id: str,
    question: str,
    course_name: str,
    term: str,
    policy: Optional[models.CoursePolicy]
) -> Dict[str, any]:
    """
    Answer a student question using RAG.

    Args:
        course_id: Course ID
        question: Student's question
        course_name: Course name
        term: Course term
        policy: Course policy configuration

    Returns:
        Dictionary with answer, sources, and refusal status
    """
    # Retrieve relevant chunks
    chunks = vector_store.query(course_id, question, n_results=5)

    # Build system prompt
    system_prompt = build_system_prompt(course_name, term, policy, chunks)

    # Call Claude
    answer = call_claude(system_prompt, question)

    # Detect refusal
    was_refused = detect_refusal(answer)

    # Format sources
    sources = []
    for chunk in chunks:
        sources.append({
            'filename': chunk['metadata'].get('filename', 'Unknown'),
            'page': chunk['metadata'].get('page', 0),
            'chunk_text': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text']
        })

    return {
        'answer': answer,
        'sources': sources,
        'was_refused': was_refused
    }
