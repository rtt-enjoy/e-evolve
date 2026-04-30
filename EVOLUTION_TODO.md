# Evolution TODO

Bot state: v1.1.0 · cycle #418 · $2.77 total · active: `llm_groq`, `articles_devto`

---

## Bugs (break current earning)

_(none open)_

---

## High Priority — Logic

_(all resolved 2026-04-30)_

---

## High Priority — UI

_(all resolved 2026-04-30)_

### 7. Evolution LLM failures show truncated unreadable error ✅
Fixed in `bot/dashboard.py`: regex-extracts `message` from nested error dict; renders `<strong>Error Type:</strong> clean message` in a red callout block below the evolution summary.

### 8. Failed article actions render as empty links ✅
Fixed in `bot/dashboard.py` action table: failures render as `<span class="err">platform — error</span>` instead of `<a>` with empty href/title.

### 9. Earnings sparkline too small for trend detection ✅
Fixed in `bot/earnings.py`: history expanded to 48 entries; only non-zero cycles appended (avoids flat line during downtime). Sparkline label updated to "Last N earning cycles".

### 10. No distinct alert when evolution is skipped vs LLM failed ✅
Fixed in `bot/dashboard.py`: derives `evo_status` (`ok|skipped|llm_error|apply_error`) from `last_evolution` fields at render time. Badge injected inline after summary text: green/grey/red/yellow.

---

## Low Priority

- `bot/earnings.py:49` — `pnl_usd` field assumed float; missing field crashes tally. Add `float(action.get('pnl_usd') or 0)`.
- `bot/llm.py:83–86` — 413 truncation cuts to 60% of bytes mid-function. Consider truncating at last newline to avoid broken code context.
- Dashboard action table shows only last 12 entries — older failures invisible. Consider paginating or linking to `earnings-log.md`.

---

## Do Not Touch

- `.github/workflows/evolve.yml` — heartbeat, never evolve
- Safety boundaries in `bot/evolution.py` — hardcoded, intentional
