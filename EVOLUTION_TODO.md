# Evolution TODO

Bot state: v1.1.1 · cycle #431 · $2.77 total · active: `llm_gemini`, `llm_openrouter`, `llm_groq` added

---

## Bugs (break current earning)

_(none open)_

---

## High Priority — Earning

- **Re-activate `articles_devto`** — was responsible for $2.65 of $2.77 total (96% of earnings).
  Add `DEV_TO_API_KEY` secret → GitHub → Settings → Secrets and variables → Actions.
  Estimated: ~$1/week when active.

- **Add `MEDIUM_INTEGRATION_TOKEN`** — dual-publish same articles to Medium at zero extra LLM cost.
  Estimated: ~$0.02/article extra.

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

- **Dashboard lacks earnings analysis** — fixed 2026-05-01.

- **Articles topic list dated** — fixed 2026-05-01.

- **Add Gemini + OpenRouter to role-based routing** — fixed 2026-05-02.
  Gemini → hard thinking (evolution), Groq → fast replies, OpenRouter → experiment.
  Dashboard shows per-role provider pills with distinct colors.
  `llm_roles` persisted in status.json.
