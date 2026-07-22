# System block diagram

Bedtime story agent: user → storyteller → **hybrid judge** (code + LLM) → retry or deliver → optional user revision.

```text
┌────────────┐
│    User    │
│  request / │
│  revise    │
└─────┬──────┘
      │ 1. bedtime request (or change notes)
      ▼
┌──────────────────────────────────────────────────────────────┐
│                    Orchestrator (main)                        │
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
│  │ 300–800      │  │ fidelity /      │  │    │
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

## Prompt / interaction flow

| Step | From → To | What moves |
|------|-----------|------------|
| 1 | User → Orchestrator | Free-text bedtime request |
| 2 | Orchestrator → Storyteller | Request + optional judge/user feedback |
| 3 | Storyteller → Hybrid Judge | Full draft (title + story) |
| 4a | Code → Orchestrator | Deterministic word count / length gate |
| 4b | LLM Judge → Orchestrator | Soft scores (safety, arc, fidelity, engage) + critique |
| 5 | Orchestrator → Storyteller | On fail: regenerate with combined feedback (≤2 attempts) |
| 6 | Orchestrator → User | Story + compact score line |
| 7 | User → Orchestrator | Optional revisions; loop until Enter |
