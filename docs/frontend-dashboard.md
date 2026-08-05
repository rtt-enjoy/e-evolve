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
`OPENROUTER_API_KEY` may be rendered so setup remains actionable, but actual
secret values must never be written to tracked status files, built assets, or
logs.

## Information Architecture

The dashboard is a multi-page shell: a fixed sidebar plus hash routes
(`#/leads`, `#/leads/3`). Each route is code-split, so the first paint loads
only the Overview chunk. Depth is deliberate — the landing page carries only
essentials, and detail lives one click away.

| Route       | Answers                                                          |
|-------------|------------------------------------------------------------------|
| `#/overview`| Is it earning, is it fresh, what needs attention right now?       |
| `#/leads`   | Which opportunities exist, worth what, and what is the first step?|
| `#/research`| Which free AI services and earning playbooks were found?          |
| `#/engine`  | Which model serves which role, and what did the last cycle do?    |
| `#/health`  | Freshness, integration readiness, errors, blocked payouts.        |
| `#/data`    | Every snapshot field, including keys no section claims yet.       |

`#/leads/<index>` is a detail view carrying the lead's `codex_prompt` and
`outreach_draft` with copy buttons. Outreach is never sent automatically.

## Section Registry

`frontend/src/sections/registry.ts` is the mechanism that keeps this dashboard
current as the bot evolves. Each section declares the `status.json` paths it
consumes, and two behaviours follow:

1. A section whose declared paths are all empty is **hidden from the nav**, so
   routes never lead to a blank page.
2. Every top-level key claimed by some section is *known*. Keys the bot starts
   emitting later are **unclaimed**, and the Data section renders them
   generically through `JsonNode` — with a "N new" badge in the sidebar.

**New backend fields therefore appear in the UI with no frontend change.** When
a new field deserves a first-class view, add its key to the relevant section's
`keys` array and render it; that removes it from the unclaimed list.

## Required Signals

The Overview must answer, without scrolling:

- Is the cycle fresh, late, or stalled?
- Total earned, and the value sitting in the lead pipeline.
- What needs attention, ranked, each linking to the section that resolves it.
- Which of the five phases succeeded in the last run.

## Implementation Notes

- Keep `status.json` backwards-compatible; every computed property must tolerate
  missing keys. Sections receive the whole snapshot and must not assume presence.
- Keep GitHub Pages static: no backend server. Python writes data, Vite builds
  the browser app, and the browser reads static files.
- Suggestion views prefer code-tech, dev.to, and free LLM work. `isAvoidedSuggestion`
  filters recommendations needing KYC, paid access, phone-gated APIs, or funded
  wallets.
- When adding a new module or secret, update `bot/status.py` first, then extend
  the relevant section in `frontend/src/sections/`.
- Build with `pnpm build` from `frontend/` so `docs/` holds the public artifacts.
  The prebuild step clears all hashed bundles, because section chunk names are
  open-ended and stale files would otherwise accumulate.
