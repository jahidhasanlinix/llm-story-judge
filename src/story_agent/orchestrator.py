"""generate → hybrid-judge → (fail? revise with critique) × N."""

from __future__ import annotations

from typing import Optional

from rich.console import Console

from story_agent.config import MAX_JUDGE_RETRIES
from story_agent.judge import judge_story
from story_agent.storyteller import generate_story

console = Console()


def generate_with_judge_loop(
    request: str, feedback: Optional[str] = None
) -> tuple[str, dict]:
    story, judgement = "", {}
    for attempt in range(MAX_JUDGE_RETRIES):
        label = f"draft {attempt + 1}/{MAX_JUDGE_RETRIES}"
        with console.status(
            f"[bold cyan]Writing…[/] ({label})",
            spinner="dots",
        ):
            story = generate_story(request, feedback=feedback)
        with console.status(
            f"[bold magenta]Judging…[/] ({label})",
            spinner="moon",
        ):
            judgement = judge_story(story, request=request)
        if judgement.get("overall_pass"):
            break
        feedback = judgement.get("feedback")
        console.print(
            f"[dim]Draft {attempt + 1} needs a tweak — rewriting…[/]"
        )
    return story, judgement
