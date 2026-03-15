"""LLM client with Groq and Gemini providers for structured output."""
import os
import json
import asyncio
import logging
from typing import TypeVar, Type
from pydantic import BaseModel

from app.notifications import fire_and_forget as notify

T = TypeVar("T", bound=BaseModel)
log = logging.getLogger(__name__)

_client = None
_provider = None

MAX_RETRIES = 3
RETRY_BASE_DELAY = 15  # seconds

REASONING_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "gemini": "gemini-2.5-pro",
}


def get_reasoning_model() -> str:
    """Return the reasoning model name for the active provider."""
    provider = _get_provider()
    return REASONING_MODELS.get(provider, "gemini-2.5-pro")


def _get_provider() -> str:
    """Detect and cache the LLM provider from environment variables."""
    global _provider
    if _provider is None:
        explicit = os.environ.get("LLM_PROVIDER", "").lower()
        if explicit in ("gemini", "groq"):
            _provider = explicit
        elif os.environ.get("GROQ_API_KEY"):
            _provider = "groq"
        elif os.environ.get("GEMINI_API_KEY"):
            _provider = "gemini"
        else:
            raise RuntimeError("Set GEMINI_API_KEY or GROQ_API_KEY")
    return _provider


def _get_client():
    """Initialize and cache the LLM client instance."""
    global _client
    if _client is not None:
        return _client

    provider = _get_provider()
    if provider == "groq":
        from groq import Groq
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    else:
        from google import genai
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def _schema_to_json_instruction(schema: Type[BaseModel]) -> str:
    """Convert a Pydantic schema to a JSON string for LLM instructions."""
    return json.dumps(schema.model_json_schema(), indent=2)


def _is_rate_limit_error(e: Exception) -> bool:
    """Check if an exception indicates a rate limit error."""
    err_str = str(e).lower()
    return "429" in err_str or "rate_limit" in err_str or "resource_exhausted" in err_str


async def generate_structured(
    prompt: str,
    response_schema: Type[T],
    model: str = None,
    temperature: float = 0.2,
) -> T:
    """Send a prompt to the LLM and return a validated Pydantic object."""
    provider = _get_provider()
    client = _get_client()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if provider == "groq":
                model = model or os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
                schema_json = _schema_to_json_instruction(response_schema)
                system_msg = (
                    "You are a data scientist. Respond with valid JSON only, "
                    "matching this schema exactly:\n" + schema_json
                )
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("LLM returned empty response")
                parsed = json.loads(content)
                return response_schema.model_validate(parsed)
            else:
                from google.genai import types
                model = model or os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=response_schema,
                        temperature=temperature,
                    ),
                )
                text = response.text
                if not text:
                    raise ValueError("LLM returned empty response")
                parsed = json.loads(text)
                return response_schema.model_validate(parsed)
        except Exception as e:
            if _is_rate_limit_error(e) and attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * attempt
                log.warning(f"Rate limit hit (attempt {attempt}/{MAX_RETRIES}), retrying in {delay}s")
                await asyncio.sleep(delay)
                continue
            notify("LLM call failed", f"provider={provider}, model={model}, error={e}")
            raise
