# System block diagram

Bedtime story agent: user → **request safety gate** → storyteller → **hybrid story judge** (code + LLM) → retry or deliver → optional user revision.

```text
┌────────────┐
│    User    │
│  request / │
│  revise    │
└─────┬──────┘
      │ 1. bedtime request (or change notes)
      ▼
┌──────────────────────────────────────────────────────────────┐
│                    Orchestrator (src/story_agent)              │
│         generate_with_judge_loop  +  user feedback loop       │
└─────────────┬────────────────────────────────▲───────────────┘
              │ 2. generate / revise           │ 6. story + scores
              ▼                                │
┌─────────────────────────┐                    │
│  Storyteller (LLM)      │                    │
│  gpt-3.5-turbo          │                    │
│  system: author voice   │                    │
│  user: request + arc    │                    │
│  temp=0.8               │                    │
│  (+ judge/user feedback)│                    │
└─────────────┬───────────┘                    │
              │ 3. draft                       │
              ▼                                │
┌─────────────────────────────────────────┐    │
│           Hybrid Judge                  │    │
│  ┌──────────────┐  ┌─────────────────┐  │    │
│  │ Code gate    │  │ LLM gate        │  │    │
│  │ word_count   │  │ safety / arc /  │  │    │
│  │ 100–250      │  │ lesson / fidel. │  │    │
│  │              │  │ engage 1–5      │  │    │
│  │ (measurable) │  │ temp=0.0        │  │    │
│  └──────┬───────┘  └────────┬────────┘  │    │
│         └─────────┬─────────┘           │    │
│                   ▼                     │    │
│         overall_pass = both ok          │    │
└───────────────────┬─────────────────────┘    │
                    │ 4. judgement + feedback  │
                    ▼                          │
              ┌───────────┐                    │
              │  pass?    │                    │
              └─────┬─────┘                    │
         no │               │ yes              │
            ▼               └──────────────────┘
   ┌────────────────┐
   │ Retry ≤ 2 with │──► storyteller (step 2)
   │ judge feedback │
   └───────┬────────┘
           │ retries exhausted
           └───────────────────► user (step 6)
                                      │
                                      ▼
                            keep / request changes
```

Before step 2, an **LLM request gate** blocks unsafe asks (blood, death, terror) with a clear `FAIL` so the storyteller cannot quietly rewrite them into a PASS.

## Prompt / interaction flow

| Step | From → To | What moves |
|------|-----------|------------|
| 1 | User → Orchestrator | Free-text bedtime request |
| 1b | Request gate → User | If unsafe: `FAIL` + reason; stop (no story) |
| 2 | Orchestrator → Storyteller | Request + optional judge/user feedback |
| 3 | Storyteller → Hybrid Judge | Full draft (title + story) |
| 4a | Code → Orchestrator | Deterministic word count / length gate |
| 4b | LLM Judge → Orchestrator | Soft scores (safety, arc, fidelity, engage) + critique |
| 5 | Orchestrator → Storyteller | On fail: regenerate with combined feedback (≤2 attempts) |
| 6 | Orchestrator → User | Story + compact score line |
| 7 | User → Orchestrator | Optional revisions; loop until Enter |
