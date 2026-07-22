"""Judge system + evaluation prompt templates."""

JUDGE_SYSTEM = (
    "You are a strict children's-book editor and child-safety reviewer. "
    "Be concrete and picky. Return raw JSON only — no markdown fences."
)

JUDGE_PROMPT = """Evaluate this bedtime story for a child aged 5–10.

CHILD'S REQUEST:
\"\"\"
{request}
\"\"\"

STORY:
\"\"\"
{story}
\"\"\"

Score ONLY these soft criteria (length is checked separately in code):
- age_appropriate (bool): no violence, fear, death, or vocab too advanced
- has_clear_arc (bool): inviting opening, soft problem, peak, satisfying
  resolution, and a calm bedtime ending
- has_clear_lesson (bool): one clear gentle lesson a child can take away
  (sharing, kindness, curiosity, unity/teamwork, bravery, honesty, patience,
  etc.). The lesson may be spoken warmly ("And that is how we learn…") —
  that is good. False if there is no lesson, or if it is muddled, scary, or
  a stiff lecture slogan only with no story feeling.
- request_faithful (bool): honors the child's specific request (names/themes).
  If the request is empty/unknown, set true only when the story is a coherent
  gentle bedtime tale; otherwise judge against the request strictly.
- engaging_score (int 1–5): 1=flat/generic/templated, 3=solid, 5=delightful
  to hear aloud like a human storyteller.
  Reward: natural spoken rhythm, expressive wonder, sensory detail, and one
  surprising but gentle memorable image.
  Cap at 3 if the opening is a stiff catalog line ("In the heart of X lived Y")
  or the closer is a lecture formula ("And so, the lesson X learned was clear").
  A warm natural moral wrap-up does NOT lower the score.
- feedback (string): 2–3 actionable sentences if anything fails; brief praise
  if all soft criteria look good

Return ONLY this JSON shape:
{{
  "age_appropriate": true,
  "has_clear_arc": true,
  "has_clear_lesson": true,
  "request_faithful": true,
  "engaging_score": 4,
  "feedback": "..."
}}"""
