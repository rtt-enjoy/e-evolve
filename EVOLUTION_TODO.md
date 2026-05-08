# Evolution TODO

Bot state: v1.23.0 - cycle #463 - $2.77 total - active: `llm_gemini`, `llm_openrouter`, `llm_groq`, `articles_devto`, `usdt_wallet`

---

## Bugs (break current earning)

_(none open)_

---

## High Priority - Earning

_(none open)_

---

## High Priority - UI

_(none open)_

---

## Low Priority

_(none open)_

---

## Do Not Touch

- `.github/workflows/evolve.yml` - heartbeat, never evolve
- Safety boundaries in `bot/evolution.py` - hardcoded, intentional

---

## Resolved

- **Workflow dependency install listed stdlib modules** - fixed 2026-05-08. Replaced `json`, `pathlib`, and `logging` with the real packages required by the active LLM and earning modules.

- **Article publishes had zero tracked value** - fixed 2026-05-08. Successful dev.to and Medium publishes now use configurable estimated value via `articles.estimated_usd_per_publish`.

- **Groq TPD rate limit blocks evolution** - fixed by adding `ANTHROPIC_API_KEY` secret.

- **Dashboard lacks earnings analysis** - fixed 2026-05-01.

- **Articles topic list dated** - fixed 2026-05-01.

- **Add Gemini + OpenRouter to role-based routing** - fixed 2026-05-02.
  Gemini -> hard thinking (evolution), Groq -> fast replies, OpenRouter -> experiment.
  Dashboard shows per-role provider pills with distinct colors.
  `llm_roles` persisted in status.json.

- **Re-activate `articles_devto`** - active as of v1.3.0 (cycle #440). `DEV_TO_API_KEY` secret present.

- **Earnings breakdown resets on week rollover** - fixed 2026-05-02. Previously accumulated all-time.

- **Evolution dashboard showed `ok` for no-change cycles** - fixed 2026-05-02. Now shows `idle` (blue).

- **Evolution LLM prompt included earnings history + last_earning** - fixed 2026-05-02. Stripped before send.

- **Add `MEDIUM_INTEGRATION_TOKEN`** - fixed in v1.22.0. Dual-publishes the same generated article to Medium when the secret is present, with no extra article generation call.

- **Dashboard frontend lacked a ranked revenue focus** - fixed in v1.22.1. Added a responsive Research & Revenue Focus section and moved provider/warning colors back through `:root` variables.

- **Article volume strategy was ignored** - fixed 2026-05-08. The orchestrator now reads `articles.per_cycle` from `config/strategy.json` for normal cycles, while owner `force articles N` commands still override it.
