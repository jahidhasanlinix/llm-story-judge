"""Small text helpers shared across the agent."""

from __future__ import annotations

import json
import re


def extract_json(text: str) -> dict:
    """Models often wrap JSON in prose or ``` fences. Take the first {...}."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in model output:\n{text}")
    return json.loads(match.group(0))


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))
