# Frontend Dashboard Contract

`docs/index.html` is the public GitHub Pages dashboard. It is built from the
React/Vite/Tailwind app in `frontend/`, while `bot/dashboard.py` publishes the
safe data files during Phase 5 of every cycle. The browser polls
`docs/status.json` every 60 seconds so new status appears without a page reload.

## Source Of Truth

Do not edit `docs/index.html` or built `docs/assets/*` files directly unless
you are updating generated output for the current commit. Durable dashboard UI
changes belong in `frontend/src/`. Durable dashboard data contract changes
belong in `bot/dashboard.py` and the status-producing backend modules.

The dashboard must represent safe status only. Secret names such as
`TWITTER_API_KEY` may be rendered so setup remains actionable, but actual secret
values must never be written to tracked status files, built assets, or logs.

## Required Frontend Signals

The first screen should answer these questions clearly:

- Is the workflow fresh, late, stalled, or offline?
- Which phase currently needs attention: status, commands, evolution, earning,
  or update?
- Which earning and model modules are active, inactive, or partially configured?
- What changed in the latest evolution, and did it produce errors?
- What actions ran in the latest earning cycle, and which failed?
- What errors, suggestions, and setup gaps should the owner act on next?
- Which integrations are active, inactive, or missing required secret names?

## Dashboard Panels

- **Workflow Status**: phase-by-phase health derived from `last_run`,
  `last_evolution`, `last_earning.actions`, `errors`, and cycle timing.
- **Live Refresh**: in-browser polling of the latest status snapshot with a
  visible last-polled timestamp and refresh control.
- **Problems And Corrections**: ranked operational issues combining stale
  workflow state, errors, failed actions, evolution failures, and missing
  high-impact setup secrets.
- **Secret Readiness**: per-feature readiness by secret name. It must never
  expose secret values.
- **Last Evolution**: latest summary, changed files, error label, and ranked
  suggestions including activation steps when present.
- **No-ID Free Path**: suggestion views should prefer code-tech, dev.to, and
  free LLM work, while filtering recommendations that require Binance KYC,
  Claude/Anthropic paid access, phone-gated Twitter/X APIs, funded wallets, or
  paid-only services.

## Implementation Notes

- Keep `status.json` backwards-compatible; every dashboard computed property must
  tolerate missing keys.
- Keep GitHub Pages static: no backend server. Python writes data, Vite builds
  the browser app, and the browser reads static files.
- When adding a new module or secret, update `bot/status.py` first, then extend
  labels and panels in `frontend/src/`.
- If a new status field helps users diagnose a problem, persist it in
  `status.json` and render it in the relevant panel rather than hiding it in
  workflow logs only.
- Build frontend changes with `npm run build` from `frontend/` so `docs/`
  contains the public GitHub Pages artifacts.
