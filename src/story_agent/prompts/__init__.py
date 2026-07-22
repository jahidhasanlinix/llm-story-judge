"""Prompt templates for the storyteller and judge."""

from story_agent.prompts.judge import JUDGE_PROMPT, JUDGE_SYSTEM
from story_agent.prompts.request_gate import REQUEST_GATE_PROMPT, REQUEST_GATE_SYSTEM
from story_agent.prompts.storyteller import (
    REVISION_NOTE,
    STORY_PROMPT,
    STORYTELLER_SYSTEM,
)

__all__ = [
    "STORYTELLER_SYSTEM",
    "STORY_PROMPT",
    "REVISION_NOTE",
    "JUDGE_SYSTEM",
    "JUDGE_PROMPT",
    "REQUEST_GATE_SYSTEM",
    "REQUEST_GATE_PROMPT",
]
