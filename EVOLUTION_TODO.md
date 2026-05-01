# Evolution TODO

Bot state: v1.1.1 · cycle #431 · $2.77 total · active: `llm_groq`, `articles_devto`

---

## Bugs (break current earning)

_(none open)_

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

---

## Resolved

- **Groq TPD rate limit blocks evolution** — fixed by adding `ANTHROPIC_API_KEY` secret.
  `llm.py` already prioritises Anthropic over Groq. No code change needed.
  **To trigger immediately after adding the secret:** commit any change to `command.txt`.
  The workflow now fires on `push` to that file (added to `evolve.yml`).
