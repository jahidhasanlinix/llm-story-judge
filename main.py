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

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from story_agent.cli import main


if __name__ == "__main__":
    main()
