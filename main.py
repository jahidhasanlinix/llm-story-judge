import os
import json
import re
from typing import Optional

from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

load_dotenv()

console = Console()
client = OpenAI()

"""
Before submitting the assignment, describe here in a few sentences what you
would have built next if you spent 2 more hours on this project:

I'd stand up a tiny offline eval harness: a fixed set of ~15 bedtime requests
(silly / scary-edge / sparse / revision-heavy), run the full generate→judge
loop with call_model mocked or live, and track pass rate, retry count, and
judge–human agreement on a hand-labeled subset so the rubric can be tuned
against reality. I'd also add an agentic unit suite that asserts the loop
feeds judge feedback on fail, stops at MAX_JUDGE_RETRIES, and fails open on
unparsable judge JSON — the control-flow bugs that matter more than prompt
wording. Last, a short read-aloud pacing pass (one cheap LLM call) to insert
natural paragraph breaks for actual bedtime use.
"""

MODEL = "gpt-3.5-turbo"  # assignment: do not change the model
MAX_JUDGE_RETRIES = 2
MIN_WORDS, MAX_WORDS = 300, 800
MIN_ENGAGING = 3

# --- model I/O -------------------------------------------------------------
def call_model(
    prompt: str,
    *,
    system: Optional[str] = None,
    max_tokens: int = 3000,
    temperature: float = 0.1,
) -> str:
    """Roles stay separated so the storyteller can be creative while the judge stays cold and strict."""
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set."
        )
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    content = resp.choices[0].message.content
    if not content:
        raise RuntimeError("Model returned empty content.")
    return content


def extract_json(text: str) -> dict:
    """Models often wrap JSON in prose or ``` fences. Take the first {...}."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in model output:\n{text}")
    return json.loads(match.group(0))


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


# --- storyteller -----------------------------------------------------------
STORYTELLER_SYSTEM = (
    "You are a warm, skilled children's bedtime author for ages 5–10. "
    "You write vivid but gentle prose. You never include violence, death, "
    "gore, real terror, or romance beyond simple friendship. "
    "Output only a short title and the story — no preamble, no notes."
)

STORY_PROMPT = """Write a bedtime story for this request:

"{request}"

Silently choose the story kind that fits best (adventure, friendship, silly,
mystery, gentle/calming, fantasy, …). Do not name that choice — let it shape
tone, pacing, and stakes.

Story arc (follow this shape):
1. Cozy introduction of character(s) and setting.
2. A gentle spark of curiosity or soft problem (never scary).
3. One or two small rising moments.
4. The character faces it with courage, kindness, cleverness, or teamwork.
5. Resolution with a small positive feeling or lesson.
6. Soft landing suitable for falling asleep — slower sentences, quieter images.

Craft rules:
- Vocabulary a 5–10 year old can follow; short paragraphs.
- Target length: about 400–700 words.
- Include the child's request concretely (names, creatures, places they asked for).
{revision_note}"""

REVISION_NOTE = """
This is a revision. Rewrite the full story from scratch, still following the
arc and craft rules, and specifically fix:
"{feedback}"
"""


def generate_story(request: str, feedback: Optional[str] = None) -> str:
    revision = REVISION_NOTE.format(feedback=feedback) if feedback else ""
    prompt = STORY_PROMPT.format(request=request, revision_note=revision)
    # Higher temperature → more varied bedtime tales; judge stays at 0.0.
    return call_model(
        prompt,
        system=STORYTELLER_SYSTEM,
        temperature=0.8,
        max_tokens=1200,
    )


# --- judge --------------------------------------------------------
JUDGE_SYSTEM = (
    "You are a strict children's-book editor and child-safety reviewer. "
    "Be concrete and picky. Return raw JSON only — no markdown fences."
)

JUDGE_PROMPT = """Evaluate this bedtime story for a child aged 5–10.

STORY:
\"\"\"
{story}
\"\"\"

Score ONLY these soft criteria (length is checked separately in code):
- age_appropriate (bool): no violence, fear, death, or vocab too advanced
- has_clear_arc (bool): intro, soft problem, peak, satisfying resolution,
  and a calm bedtime ending
- request_faithful (bool): honors the child's specific request (names/themes)
- engaging_score (int 1–5): 1=flat/generic, 3=solid, 5=delightful to hear aloud
- feedback (string): 2–3 actionable sentences if anything fails; brief praise
  if all soft criteria look good

Return ONLY this JSON shape:
{{
  "age_appropriate": true,
  "has_clear_arc": true,
  "request_faithful": true,
  "engaging_score": 4,
  "feedback": "..."
}}"""


def judge_story(story: str) -> dict:
    """Hybrid judge: code owns length; LLM owns taste + safety + fidelity."""
    words = word_count(story)
    length_ok = MIN_WORDS <= words <= MAX_WORDS

    try:
        raw = call_model(
            JUDGE_PROMPT.format(story=story),
            system=JUDGE_SYSTEM,
            temperature=0.0,
            max_tokens=300,
        )
        scores = extract_json(raw)
    except (ValueError, json.JSONDecodeError, OpenAIError) as exc:
        return {
            "word_count": words,
            "appropriate_length": length_ok,
            "age_appropriate": True,
            "has_clear_arc": True,
            "request_faithful": True,
            "engaging_score": None,
            "overall_pass": length_ok,
            "feedback": f"(judge unavailable: {type(exc).__name__}; length-only gate)",
        }

    engaging = int(scores.get("engaging_score") or 0)
    soft_ok = (
        bool(scores.get("age_appropriate"))
        and bool(scores.get("has_clear_arc"))
        and bool(scores.get("request_faithful"))
        and engaging >= MIN_ENGAGING
    )
    overall = soft_ok and length_ok

    feedback = scores.get("feedback") or ""
    if not length_ok:
        length_note = (
            f"Length is {words} words; rewrite to land between "
            f"{MIN_WORDS}–{MAX_WORDS}."
        )
        feedback = f"{feedback} {length_note}".strip()

    return {
        "word_count": words,
        "appropriate_length": length_ok,
        "age_appropriate": bool(scores.get("age_appropriate")),
        "has_clear_arc": bool(scores.get("has_clear_arc")),
        "request_faithful": bool(scores.get("request_faithful")),
        "engaging_score": engaging,
        "overall_pass": overall,
        "feedback": feedback,
    }


# --- orchestration ---------------------------------------------------------
def generate_with_judge_loop(
    request: str, feedback: Optional[str] = None
) -> tuple[str, dict]:
    """generate → hybrid-judge → (fail? revise with critique) × N."""
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
            judgement = judge_story(story)
        if judgement.get("overall_pass"):
            break
        feedback = judgement.get("feedback")
        console.print(
            f"[dim]Draft {attempt + 1} needs a tweak — rewriting…[/]"
        )
    return story, judgement


def format_judge_line(j: dict) -> str:
    passed = j.get("overall_pass")
    badge = "[bold green]PASS[/]" if passed else "[bold yellow]RETRY[/]"
    return (
        f"{badge}  engage={j.get('engaging_score')}  "
        f"arc={j.get('has_clear_arc')}  "
        f"safe={j.get('age_appropriate')}  "
        f"faithful={j.get('request_faithful')}  "
        f"words={j.get('word_count')}"
    )


def main() -> None:
    console.print()
    request = Prompt.ask("[bold blue]Ask for your story[/]").strip()
    if not request:
        console.print("[yellow]No request given — ending. Goodnight![/]")
        return

    console.print()
    console.print(
        Panel(
            request,
            title="[bold blue]Your ask[/]",
            border_style="blue",
            padding=(1, 2),
        )
    )

    feedback = None
    while True:
        console.print()
        story, judgement = generate_with_judge_loop(request, feedback=feedback)

        console.print()
        console.print(
            Panel(
                Text(story),
                title="[bold green]Bedtime story[/]",
                border_style="green",
                padding=(1, 2),
            )
        )
        console.print(
            Panel(
                format_judge_line(judgement),
                title="[bold magenta]Judge[/]",
                border_style="magenta",
                padding=(0, 2),
            )
        )
        console.print()

        feedback = Prompt.ask(
            "[bold yellow]Want any changes?[/] "
            "[dim](describe them, or press Enter to finish)[/]",
            default="",
        ).strip()
        if not feedback:
            console.print()
            console.print(
                Panel.fit(
                    "[bold]Enjoy your story! Goodnight.[/] 🌙",
                    border_style="cyan",
                )
            )
            console.print()
            break

        console.print()
        console.print(
            Panel(
                feedback,
                title="[bold yellow]Your revision[/]",
                border_style="yellow",
                padding=(1, 2),
            )
        )


if __name__ == "__main__":
    main()
