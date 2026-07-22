# llm-story-judge

Bedtime story agent for ages 5–10. A storyteller LLM drafts the story; a hybrid judge (code + LLM) scores it and can request retries. You can ask for revisions until you're happy.

**System design:** see [SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md).

---

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- An [OpenAI API key](https://platform.openai.com/api-keys)

## Setup

```bash
# clone
git clone https://github.com/jahidhasanlinix/llm-story-judge.git
cd llm-story-judge

# create the project env and install deps from pyproject.toml / uv.lock
uv sync

# add your API key (never commit .env)
cp .env.example .env
# then edit .env and set:
# OPENAI_API_KEY=sk-...
```

### Optional: start from scratch with uv

If you are recreating the project yourself:

```bash
uv init
uv add openai python-dotenv rich
```

Then copy in `main.py`, set `.env`, and run as below.

## Run

```bash
uv run python main.py
```

## Example

When prompted:

```text
Ask for your story: a shy firefly who learns to share her light with forest friends
```

After the story prints (with judge scores), you can revise or finish:

```text
Want any changes?: make the ending softer and add a lullaby line
```

Press **Enter** with no text to finish.

---

Assignment brief: [README_Task.md](README_Task.md)
