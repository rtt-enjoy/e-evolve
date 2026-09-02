# Evolution TODO

Bot state: v1.36.1 - cycle #1741 - active: `llm_gemini`, `llm_openrouter`, `llm_groq`, `articles_devto`, `usdt_wallet`

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
- Research-only policy guards in `bot/main.py`, `bot/commands.py`, and
  `bot/status.py` (FEATURE_MAP) - hardcoded, intentional

---

## Resolved

- **`force articles N` ignored its own count** - fixed 2026-09-02. `commands.py`
  parsed and clamped N to 1-5 and logged it, but `articles.run()` read the
  override only as a truthy cap-bypass and always published exactly one article.
  The publish path is now `_publish_once`, looped N times and stopped at the
  first failure so a dead source pool cannot burn free-tier LLM calls.

- **Dead config files were being fed to the evolution LLM** - fixed 2026-09-02.
  `bot/evolution.py` globs `config/*.json` into the codebase snapshot.
  `config/llm_providers.json` and `config/llm_workflows.json` were not valid JSON
  (Python dict reprs) and named obsolete Gemini/Groq per-role routing;
  `config/error_handling.json` blocked `publishing`, contradicting the live
  `research_and_article_publishing` policy. All three removed, plus the unused
  `bot/utils/` package and three docs describing removed behaviour.

- **Dashboard realtime sync used root-only state** - fixed 2026-05-08. `bot/dashboard.py` now publishes `docs/status.json` and `docs/earnings-log.md` alongside the generated dashboard, and the live UI reloads when a new cycle/version arrives so every panel stays synchronized.

- **Article loop left normal earning throughput below the active cap** - fixed 2026-05-08. Raised `articles.per_cycle` to 3 and increased buyer-intent topic selection to 55% when a CTA is configured.

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

- **Add `MEDIUM_INTEGRATION_TOKEN`** - fixed in v1.22.0, then reverted in v1.34.0. Medium publishing is outside the dev.to-only policy, so the code path and secret were removed.

- **Dashboard frontend lacked a ranked revenue focus** - fixed in v1.22.1. Added a responsive Research & Revenue Focus section and moved provider/warning colors back through `:root` variables.

- **Article volume strategy was ignored** - fixed 2026-05-08. The orchestrator now reads `articles.per_cycle` from `config/strategy.json` for normal cycles, while owner `force articles N` commands still override it.
