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

### 7. Evolution LLM failures show truncated unreadable error
`docs/index.html:76` (rendered from dashboard) — shows `'error': {'message': 'Request too lar...` cut off.
**Fix:** In `bot/dashboard.py`, extract `error.message` from nested dict before truncating; show clean one-liner + error type badge.

### 8. Failed article actions render as empty links
`docs/index.html:84` — failed article actions have empty `title` and `url`, producing blank clickable `<a>` tags.
**Fix:** In `bot/dashboard.py` action table, render failures as `<span class="error">platform — {error}</span>` instead of a link.

### 9. Earnings sparkline too small for trend detection
`bot/dashboard.py:153–155` — history capped at 10 cycles (~10 hours). Visual trend meaningless at that scale.
**Fix:** Expand history to 48 entries (2 days). Keep only non-zero cycles to avoid flat line during downtime.

### 10. No distinct alert when evolution is skipped vs LLM failed
Dashboard shows same "Last Evolution" block whether evolution was skipped by command, hit token limit, or crashed. No visual distinction.
**Fix:** Add `evolution_status` field to status.json (`ok|skipped|llm_error|apply_error`). Dashboard renders badge: green/grey/red/yellow.

---

## Low Priority

- `bot/earnings.py:49` — `pnl_usd` field assumed float; missing field crashes tally. Add `float(action.get('pnl_usd') or 0)`.
- `bot/llm.py:83–86` — 413 truncation cuts to 60% of bytes mid-function. Consider truncating at last newline to avoid broken code context.
- Dashboard action table shows only last 12 entries — older failures invisible. Consider paginating or linking to `earnings-log.md`.

---

## Do Not Touch

- `.github/workflows/evolve.yml` — heartbeat, never evolve
- Safety boundaries in `bot/evolution.py` — hardcoded, intentional
