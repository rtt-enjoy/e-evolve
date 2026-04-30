# Evolution TODO

Bot state: v1.1.0 · cycle #418 · $2.77 total · active: `llm_groq`, `articles_devto`

---

## Bugs (break current earning)

_(none open)_

---

## High Priority — Logic

### 1. Evolution error truncated to 120 chars
`bot/evolution.py:228` truncates LLM failure message before saving to status. `bot/dashboard.py:87–99` only shows what's saved — user can't tell if failure was token limit, bad JSON, or API error.
**Fix:** Save full error string (or first 500 chars) + error type tag (`413|json|api`) to status.json.

### 2. Codebase snapshot silently truncated → LLM edits unseen code
`bot/evolution.py:135–138` stops adding files once budget is exceeded but doesn't tell LLM which files were omitted. LLM can propose changes to files it never read.
**Fix:** Append a `# OMITTED FILES: [list]` comment to the snapshot so LLM knows what it can't touch.

### 3. Medium posting has no retry; dev.to ignores rate-limit headers
`bot/earning/articles.py:164` — Medium: zero retries on transient failures.
`bot/earning/articles.py:155–159` — dev.to: retries after flat 3s, ignores `X-RateLimit-Reset` header on 429.
**Fix:** Add 2-retry loop to Medium. On dev.to 429, parse `Retry-After` header and sleep that duration.

### 4. Article generation failure reason not captured
`bot/earning/articles.py:111–123` catches all exceptions as one message. Dashboard shows "Generation failed" with no signal whether it's LLM timeout, quota, or JSON parse error.
**Fix:** Distinguish exception types; save `error_type` field (`llm_timeout|llm_json|llm_quota|unknown`) in action dict.

### 5. Status file corruption wipes all historical earnings
`bot/status.py:38–39` — corrupt JSON triggers reset to clean defaults, losing total earnings, version, suggestions.
**Fix:** On parse failure, write corrupt file to `status.json.corrupt`, then load defaults. Never silently discard.

### 6. Git commit fails silently, cycle state lost
`bot/git_utils.py:41–52` — commit failure is caught and logged but caller doesn't know. Cycle runs, earnings logged, but nothing persists.
**Fix:** Return structured result; in `bot/main.py` Phase 5 log a visible `[GIT FAIL]` warning to errors list so dashboard shows it.

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
