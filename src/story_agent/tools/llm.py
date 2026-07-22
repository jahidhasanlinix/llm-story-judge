"""OpenAI chat wrapper used by storyteller and judge."""

from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI

from story_agent.config import MODEL

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def call_model(
    prompt: str,
    *,
    system: Optional[str] = None,
    max_tokens: int = 3000,
    temperature: float = 0.1,
) -> str:
    """Roles stay separated so the storyteller can be creative while the judge stays cold and strict."""
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = get_client().chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    content = resp.choices[0].message.content
    if not content:
        raise RuntimeError("Model returned empty content.")
    return content
