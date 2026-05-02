# Evolution TODO

Bot state: v1.1.1 · cycle #431 · $2.77 total · active: `llm_gemini`, `llm_openrouter`, `llm_groq` added

---

## Bugs (break current earning)

_(none open)_

---

## High Priority — Earning

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

- **Re-activate `articles_devto`** — active as of v1.3.0 (cycle #440). `DEV_TO_API_KEY` secret present.

- **Earnings breakdown resets on week rollover** — fixed 2026-05-02. Previously accumulated all-time.

- **Evolution dashboard showed `ok` for no-change cycles** — fixed 2026-05-02. Now shows `idle` (blue).

- **Evolution LLM prompt included earnings history + last_earning** — fixed 2026-05-02. Stripped before send.
