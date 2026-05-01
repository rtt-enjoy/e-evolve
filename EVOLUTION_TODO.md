# Evolution TODO

Bot state: v1.1.0 · cycle #428 · $2.77 total · active: `llm_groq`, `articles_devto`

---

## Bugs (break current earning)

- **Groq TPD rate limit blocks evolution** — hitting 100k token/day cap on `llama-3.3-70b-versatile`. Evolution skips with 429. Options: add `ANTHROPIC_API_KEY` secret (priority-selected over Groq), or reduce codebase context sent per cycle.

---

## High Priority — Logic

_(none open)_

---

## High Priority — UI

_(none open)_

---

## Low Priority

_(none open)_

---

## Do Not Touch

- `.github/workflows/evolve.yml` — heartbeat, never evolve
- Safety boundaries in `bot/evolution.py` — hardcoded, intentional
