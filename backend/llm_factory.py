"""
Single-point LLM client factory (AR-006, NFR-002).
All 5 agents obtain their LLM client from this module.
Changing LLM_MODEL_ID / LLM_PROVIDER env vars swaps the model for every agent.
"""

from anthropic import Anthropic
from backend.config import LLM_MODEL_ID, LLM_PROVIDER, ANTHROPIC_API_KEY

_client_instance = None


def get_llm_client() -> Anthropic:
    global _client_instance
    if _client_instance is None:
        if LLM_PROVIDER != "anthropic":
            raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}. Currently only 'anthropic' is supported.")
        _client_instance = Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client_instance


def get_model_id() -> str:
    return LLM_MODEL_ID


def invoke_llm(system_prompt: str, messages: list[dict], max_tokens: int = 4096) -> str:
    client = get_llm_client()
    response = client.messages.create(
        model=get_model_id(),
        max_tokens=max_tokens,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text
