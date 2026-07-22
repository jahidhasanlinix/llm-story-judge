# llm-story-judge

Bedtime story agent for ages 5–10. A storyteller writes the story; a hybrid
code + LLM judge scores it; optional user revisions loop until you’re done.

System design diagram: [SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md)

## Demo

<video src="demo/demo.mp4" controls width="720"></video>

## Layout

```text
main.py                 # entrypoint (loads root .env)
.env                    # OPENAI_API_KEY (stays at repo root)
src/story_agent/
  config.py             # model + length / engage thresholds
  prompts/              # storyteller + judge prompt templates
  tools/                # LLM client + text helpers
  storyteller.py
  judge.py
  orchestrator.py       # generate → judge → retry loop
  cli.py                # Rich terminal UI
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- OpenAI API key

## Setup

```bash
git clone https://github.com/jahidhasanlinix/llm-story-judge.git
cd llm-story-judge

uv sync

source .venv/bin/activate

# API key
cp .env.example .env
# edit .env → OPENAI_API_KEY=sk-...
```

## Run

```bash
uv run python main.py
```

## Example query

Passed Version:

```text
Pass: a little snail who is always late but friends wait for him, about patience and kindness
```

Failed Version:

```text
Fail: bloody dragon battle where knights die screaming — make it scary for bedtime
```

Press Enter with an empty answer to finish.

Assignment brief: [README_Task.md](README_Task.md)
