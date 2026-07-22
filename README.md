# llm-story-judge

Bedtime story agent for ages 5–10. A storyteller writes the story.

System design diagram: [SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md)

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- OpenAI API key

## Setup

```bash
git clone https://github.com/jahidhasanlinix/llm-story-judge.git
cd llm-story-judge

uv init
uv add openai python-dotenv rich
uv sync

# API key
cp .env.example .env
# edit .env → OPENAI_API_KEY=sk-...
```

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
