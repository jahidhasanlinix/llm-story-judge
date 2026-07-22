"""Hybrid judge: request gate + story judge (code length + LLM soft scores)."""

from __future__ import annotations

import json

from openai import OpenAIError

from story_agent.config import MAX_WORDS, MIN_ENGAGING, MIN_WORDS
from story_agent.prompts.judge import JUDGE_PROMPT, JUDGE_SYSTEM
from story_agent.prompts.request_gate import REQUEST_GATE_PROMPT, REQUEST_GATE_SYSTEM
from story_agent.tools.llm import call_model
from story_agent.tools.text import extract_json, word_count


def screen_request(request: str) -> dict:
    """LLM gate on the ask itself — unsafe bedtime requests fail before writing."""
    try:
        raw = call_model(
            REQUEST_GATE_PROMPT.format(request=request),
            system=REQUEST_GATE_SYSTEM,
            temperature=0.0,
            max_tokens=200,
        )
        scores = extract_json(raw)
        safe = bool(scores.get("safe_for_bedtime"))
        reason = (scores.get("reason") or "").strip()
        suggest = (scores.get("suggest_safer_ask") or "").strip()
    except (ValueError, json.JSONDecodeError, OpenAIError) as exc:
        # Fail open on gate errors so a flaky parse doesn't block every story.
        return {
            "overall_pass": True,
            "age_appropriate": True,
            "has_clear_arc": None,
            "has_clear_lesson": None,
            "request_faithful": None,
            "engaging_score": None,
            "word_count": 0,
            "feedback": f"(request gate unavailable: {type(exc).__name__}; continuing)",
            "suggest_safer_ask": "",
            "gate": "request",
        }

    feedback = reason
    if not safe and suggest:
        feedback = f"{reason} Try instead: {suggest}"

    return {
        "overall_pass": safe,
        "age_appropriate": safe,
        "has_clear_arc": False if not safe else None,
        "has_clear_lesson": False if not safe else None,
        "request_faithful": False if not safe else None,
        "engaging_score": 1 if not safe else None,
        "word_count": 0,
        "feedback": feedback or (
            "Request is not safe for a gentle bedtime story."
            if not safe
            else "Request looks fine for bedtime."
        ),
        "suggest_safer_ask": suggest,
        "gate": "request",
    }


def judge_story(story: str, request: str = "") -> dict:
    words = word_count(story)
    length_ok = MIN_WORDS <= words <= MAX_WORDS

    try:
        raw = call_model(
            JUDGE_PROMPT.format(
                story=story,
                request=request or "(not provided)",
            ),
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
            "has_clear_lesson": True,
            "request_faithful": True,
            "engaging_score": None,
            "overall_pass": length_ok,
            "feedback": f"(judge unavailable: {type(exc).__name__}; length-only gate)",
            "gate": "story",
        }

    engaging = int(scores.get("engaging_score") or 0)
    soft_ok = (
        bool(scores.get("age_appropriate"))
        and bool(scores.get("has_clear_arc"))
        and bool(scores.get("has_clear_lesson"))
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
        "has_clear_lesson": bool(scores.get("has_clear_lesson")),
        "request_faithful": bool(scores.get("request_faithful")),
        "engaging_score": engaging,
        "overall_pass": overall,
        "feedback": feedback,
        "gate": "story",
    }


def format_judge_line(j: dict) -> str:
    passed = j.get("overall_pass")
    if j.get("gate") == "request" and not passed:
        badge = "[bold red]FAIL[/]"
    elif passed:
        badge = "[bold green]PASS[/]"
    else:
        badge = "[bold yellow]RETRY[/]"
    return (
        f"{badge}  engage={j.get('engaging_score')}  "
        f"arc={j.get('has_clear_arc')}  "
        f"lesson={j.get('has_clear_lesson')}  "
        f"safe={j.get('age_appropriate')}  "
        f"faithful={j.get('request_faithful')}  "
        f"words={j.get('word_count')}"
    )
