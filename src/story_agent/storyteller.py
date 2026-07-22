"""Generate bedtime stories from a child request (+ optional revision notes)."""

from __future__ import annotations

from typing import Optional

from story_agent.prompts.storyteller import (
    REVISION_NOTE,
    STORY_PROMPT,
    STORYTELLER_SYSTEM,
)
from story_agent.tools.llm import call_model


def generate_story(request: str, feedback: Optional[str] = None) -> str:
    revision = REVISION_NOTE.format(feedback=feedback) if feedback else ""
    prompt = STORY_PROMPT.format(request=request, revision_note=revision)
    # Higher temperature → more varied bedtime tales; judge stays at 0.0.
    return call_model(
        prompt,
        system=STORYTELLER_SYSTEM,
        temperature=0.8,
        max_tokens=600,
    )
