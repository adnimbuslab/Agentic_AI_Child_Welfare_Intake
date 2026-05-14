"""
Single-point LLM client factory (AR-006, NFR-002).
All 5 agents obtain their LLM client from this module.
Changing LLM_MODEL_ID / LLM_PROVIDER env vars swaps the model for every agent.
"""

import json
import re
import requests
from backend.config import LLM_MODEL_ID, LLM_PROVIDER, ANTHROPIC_API_KEY, GOOGLE_API_KEY, OLLAMA_BASE_URL


def get_model_id() -> str:
    return LLM_MODEL_ID


def parse_llm_json(raw: str) -> dict:
    """Parse JSON from LLM output, handling common quirks like comments, markdown fencing, and trailing commas."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
    # Strip single-line // comments (not inside strings)
    cleaned = re.sub(r'(?<=[,\}\]\d"null true false])\s*//[^\n]*', '', cleaned)
    # Strip trailing commas before } or ]
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
    return json.loads(cleaned)


def invoke_llm(system_prompt: str, messages: list[dict], max_tokens: int = 4096) -> str:
    if LLM_PROVIDER == "ollama":
        return _invoke_ollama(system_prompt, messages, max_tokens)
    elif LLM_PROVIDER == "google":
        return _invoke_google(system_prompt, messages, max_tokens)
    elif LLM_PROVIDER == "anthropic":
        return _invoke_anthropic(system_prompt, messages, max_tokens)
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")


def _invoke_ollama(system_prompt: str, messages: list[dict], max_tokens: int) -> str:
    ollama_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        role = msg["role"] if msg["role"] in ("user", "assistant") else "user"
        ollama_messages.append({"role": role, "content": msg["content"]})

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": LLM_MODEL_ID,
            "messages": ollama_messages,
            "stream": False,
            "options": {"num_predict": max_tokens},
        },
        timeout=600,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def _invoke_google(system_prompt: str, messages: list[dict], max_tokens: int) -> str:
    import google.generativeai as genai

    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(
        model_name=LLM_MODEL_ID,
        system_instruction=system_prompt,
    )

    history = []
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})

    chat = model.start_chat(history=history)
    last_msg = messages[-1]["content"] if messages else ""
    response = chat.send_message(
        last_msg,
        generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens),
    )
    return response.text


def _invoke_anthropic(system_prompt: str, messages: list[dict], max_tokens: int) -> str:
    from anthropic import Anthropic

    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=LLM_MODEL_ID,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text
