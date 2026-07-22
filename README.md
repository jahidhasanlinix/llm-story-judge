# llm-story-judge

Bedtime story agent for ages 5–10. A storyteller writes the story; a hybrid judge (code + LLM) scores it and can ask for a rewrite. You can request changes until you press Enter.

System design diagram: [SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md)

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- OpenAI API key

## Setup

```bash
git clone https://github.com/jahidhasanlinix/llm-story-judge.git
cd llm-story-judge

# install deps (from pyproject.toml / uv.lock)
uv sync

# API key — do not commit .env
cp .env.example .env
# edit .env → OPENAI_API_KEY=sk-...
```

### Create a new uv project (optional)

If you are starting fresh instead of cloning:

```bash
uv init
uv add openai python-dotenv rich
```

Then add `main.py`, create `.env`, and run as below.

## Run

```bash
uv run python main.py
```

## Example query

```text
Ask for your story: a shy firefly who learns to share her light with forest friends
```

Optional revision:

```text
Want any changes?: make the ending softer and add a lullaby line
```

Press Enter with an empty answer to finish.

Assignment brief: [README_Task.md](README_Task.md)
