"""
Unified LLM Engine — Optimized for speed with cached client initialization.
Supports Groq and Google Gemini with automatic fallback.
"""
import streamlit as st
from config.settings import (
    GROQ_API_KEY, GOOGLE_API_KEY, GROQ_MODEL, GEMINI_MODEL,
    DEFAULT_PROVIDER, SYSTEM_PROMPT, MEMORY_WINDOW, MAX_CONVERSATION_MEMORY
)


@st.cache_resource
def _init_gemini_client():
    """Initialize and cache Google Gemini client (persists across reruns)."""
    from google import genai
    return genai.Client(api_key=GOOGLE_API_KEY)


@st.cache_resource
def _init_groq_client():
    """Initialize and cache Groq client (persists across reruns)."""
    from groq import Groq
    return Groq(api_key=GROQ_API_KEY)


def get_llm_client():
    """Get the cached LLM client. Uses @st.cache_resource for zero re-init overhead."""
    provider = st.session_state.get('llm_provider', DEFAULT_PROVIDER)
    try:
        if provider == "gemini" and GOOGLE_API_KEY:
            st.session_state.llm_provider = "gemini"
            return _init_gemini_client()
        elif provider == "groq" and GROQ_API_KEY:
            st.session_state.llm_provider = "groq"
            return _init_groq_client()
        elif GOOGLE_API_KEY:
            st.session_state.llm_provider = "gemini"
            return _init_gemini_client()
        elif GROQ_API_KEY:
            st.session_state.llm_provider = "groq"
            return _init_groq_client()
    except Exception:
        pass
    return None


def is_api_configured():
    """Check if at least one API key is available."""
    return bool(GOOGLE_API_KEY) or bool(GROQ_API_KEY)


def generate_response(user_message, extra_context="", conversation_memory=None):
    """Generate a response using the configured LLM provider — optimized for speed."""
    client = get_llm_client()
    if client is None:
        return "❌ No API key configured. Please set GOOGLE_API_KEY or GROQ_API_KEY in your .env file."

    provider = st.session_state.get('llm_provider', DEFAULT_PROVIDER)
    full_system_prompt = SYSTEM_PROMPT + extra_context

    # Keep memory small for speed — only last few exchanges
    memory = conversation_memory or []
    memory_slice = memory[-MEMORY_WINDOW:]

    try:
        if provider == "gemini":
            return _call_gemini(client, full_system_prompt, memory_slice, user_message)
        else:
            return _call_groq(client, full_system_prompt, memory_slice, user_message)
    except Exception as e:
        # Try fallback
        fallback = _try_fallback(provider, full_system_prompt, memory_slice, user_message)
        if fallback:
            return fallback
        return f"❌ Error: {str(e)}"


def _call_gemini(client, system_prompt, memory, user_message):
    """Fast Gemini API call."""
    from google.genai import types

    contents = []
    for mem in memory:
        contents.append({"role": "user", "parts": [{"text": mem["user"]}]})
        contents.append({"role": "model", "parts": [{"text": mem["assistant"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.5,  # Lower temp = faster + more consistent
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=config
    )
    return response.text


def _call_groq(client, system_prompt, memory, user_message):
    """Fast Groq API call."""
    messages = [{"role": "system", "content": system_prompt}]
    for mem in memory:
        messages.append({"role": "user", "content": mem["user"]})
        messages.append({"role": "assistant", "content": mem["assistant"]})
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=800,  # Shorter = faster
    )
    return response.choices[0].message.content


def _try_fallback(failed_provider, system_prompt, memory, user_message):
    """Try the other provider as fallback."""
    try:
        if failed_provider == "gemini" and GROQ_API_KEY:
            client = _init_groq_client()
            return _call_groq(client, system_prompt, memory, user_message)
        elif failed_provider == "groq" and GOOGLE_API_KEY:
            client = _init_gemini_client()
            return _call_gemini(client, system_prompt, memory, user_message)
    except Exception:
        pass
    return None


def add_to_memory(user_msg, assistant_msg):
    """Add a conversation exchange to session memory."""
    if 'conversation_memory' not in st.session_state:
        st.session_state.conversation_memory = []
    st.session_state.conversation_memory.append({
        "user": user_msg,
        "assistant": assistant_msg
    })
    # Keep memory lean for speed
    if len(st.session_state.conversation_memory) > MAX_CONVERSATION_MEMORY:
        st.session_state.conversation_memory = st.session_state.conversation_memory[-MAX_CONVERSATION_MEMORY:]

def transcribe_audio(audio_bytes):
    """Transcribe audio using Groq Whisper API for ultra-fast STT."""
    client = _init_groq_client() if GROQ_API_KEY else None
    if not client:
        return None
    try:
        # Use stream for direct bytes
        from groq.types.audio import Transcription
        transcription = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes.read()),
            model="whisper-large-v3"
        )
        return transcription.text
    except Exception as e:
        print(f"STT Error: {e}")
        return None
