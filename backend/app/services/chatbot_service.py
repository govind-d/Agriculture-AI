"""
AI Chatbot service — Gemini-powered agriculture assistant.
Adapted from smart-agriculture-ai/services/chatbot_service.py
"""

import google.generativeai as genai
from app.core.config import settings

_model = None

SYSTEM_INSTRUCTION = (
    "You are an expert agriculture AI assistant helping Indian farmers. "
    "Provide practical, actionable advice about farming, crops, fertilizers, "
    "soil health, plant diseases, irrigation, weather, and pest management. "
    "If the user asks about anything unrelated to agriculture, politely decline "
    "and steer the conversation back to farming topics. "
    "Keep responses concise and use simple language that farmers can understand. "
    "When discussing crops or practices, consider Indian agricultural conditions."
)


def _get_model():
    """Lazily initialize the Gemini model."""
    global _model
    if _model is None and settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-3.6-flash")
    return _model


def get_chatbot_response(user_message: str, chat_history: list = None) -> str:
    """
    Get a response from the Gemini agriculture chatbot.

    Args:
        user_message: The user's question
        chat_history: List of {"role": "user"|"assistant", "content": str}

    Returns:
        The assistant's response text
    """
    model = _get_model()
    if model is None:
        return (
            "AI Chatbot is not configured. Please set the GEMINI_API_KEY "
            "environment variable to enable the agriculture assistant."
        )

    # Build the full prompt with history context
    full_prompt = f"System Instruction: {SYSTEM_INSTRUCTION}\n\n"

    if chat_history:
        for msg in chat_history[-10:]:  # Keep last 10 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            full_prompt += f"{role}: {msg['content']}\n"

    full_prompt += f"User: {user_message}\nAssistant:"

    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"I'm having trouble responding right now. Please try again. (Error: {str(e)})"
