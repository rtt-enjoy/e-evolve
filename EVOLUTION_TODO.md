# Evolution TODO

Bot state: v1.1.1 · cycle #431 · $2.77 total · active: `llm_anthropic` only

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

- **Add `GROQ_API_KEY`** — free fallback LLM, eliminates single point of failure.
  Free tier at console.groq.com.

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

- **Dashboard lacks earnings analysis** — fixed 2026-05-01.
  Added: earnings projection (avg/cycle × 168), $10/week goal progress bar,
  per-platform breakdown bars, last-run age pill (green/yellow/red), cycle duration,
  two-column layout for Evolution + Inactive Modules, max-width 960px.

- **Articles topic list dated** — fixed 2026-05-01.
  Refreshed to 32 topics covering Claude 4.x, Groq, agentic AI 2026, real cycle numbers.
