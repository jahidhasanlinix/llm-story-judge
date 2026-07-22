"""Prompts for screening the child's request before storytelling."""

REQUEST_GATE_SYSTEM = (
    "You are a strict bedtime-request safety screener for ages 5–10. "
    "Return raw JSON only — no markdown fences."
)

REQUEST_GATE_PROMPT = """Decide if this bedtime STORY REQUEST is safe to fulfill
as written for a child aged 5–10.

REQUEST:
\"\"\"
{request}
\"\"\"

Mark safe_for_bedtime=false if the ask clearly wants any of:
- violence, fighting to injure/kill, blood, gore
- death, dying, screaming in terror
- real fear/horror intended to scare the child at bedtime
- cruelty, abuse, or other age-inappropriate content

Mark safe_for_bedtime=true for normal gentle kids' themes even if they include
mild pretend conflict that can be told kindly (lost toy, shy feelings, a
grumpy but harmless dragon that becomes a friend, etc.).

If unsafe, suggest_safer_ask should be one short kinder alternative the child
could try instead. If safe, suggest_safer_ask can be "".

Return ONLY this JSON shape:
{{
  "safe_for_bedtime": true,
  "reason": "one short sentence",
  "suggest_safer_ask": ""
}}"""
