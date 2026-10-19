# Frontend Dashboard Contract

`docs/index.html` is the public GitHub Pages dashboard. It is built from the
React/Vite/Tailwind app in `frontend/`, while `bot/dashboard.py` publishes the
safe data files during Phase 5 of every cycle. The browser keeps itself in
sync with the newest cycle without a reload — see **Staying In Sync** below.

## Staying In Sync

A cycle commits `docs/status.json` to `main`, but the Pages copy only changes
when the frontend workflow redeploys. A push made with the Actions token does
not trigger that workflow, so it falls back to its `:27` hourly cron, and Pages
then caches the file for 10 minutes. Read from Pages alone, the dashboard could
trail the bot by most of an hour.

`frontend/src/services/status.ts` therefore reads **both** copies — Pages and
`raw.githubusercontent.com/<github_repo>/main/docs/status.json` (public,
CORS-enabled, 5-minute cache) — and keeps whichever has the newer `last_run`.
The repo name comes from the snapshot's own `github_repo`. If the raw read
fails, Pages is used unchanged.

`frontend/src/utils/sync.ts` (`useStatusSync`) owns the polling:

- every 60 s while the tab is visible; paused while hidden; immediate refetch
  when the tab regains focus or the network returns;
- a snapshot with fewer `total_runs` than the one on screen is ignored, so the
  two copies briefly disagreeing never steps the page backwards;
- when `total_runs` increases, a **"Cycle #N landed"** notice lists what moved
  (`diffCycle`: money received, posts, views, drafts held back, a new review
  branch, errors) and tile values that changed replay their entrance;
- the top bar shows `synced Ns ago · next cycle in ~Mm` (due an hour after
  `last_run`, which is the cycle's start).

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

| Route        | Answers                                                         	  |
|--------------|--------------------------------------------------------------------|
| `#/overview` | Is it earning, is it fresh, what needs attention right now?        |
| `#/reach`    | What was published, who read it, does every reader see the ask?    |
| `#/leads`    | Which opportunities exist, worth what, and what is the first step? |
| `#/research` | Which free AI services and earning playbooks were found?           |
| `#/engine`   | Which model served each role, and what did evolution propose?      |
| `#/health`   | Freshness, integration readiness, errors, receive-wallet state.    |
| `#/data`     | Every snapshot field, including keys no section claims yet.        |

`#/leads/<index>` is a detail view carrying the lead's `codex_prompt` with a
copy button.

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
- Earnings confirmed on-chain.
- The reader → ask → wallet funnel (`buildFunnel`): views, posts observed to
  carry the ask (from `receipt_check`, never `backfill`), money received — and
  a verdict saying *why* the figure is what it is. `$0.00` because nobody
  tipped and `$0.00` because no ask shipped need opposite fixes.
- What needs attention, ranked, each linking to the section that resolves it.
- Which of the five phases succeeded in the last run (`buildPhases`, shared
  with Health).

Two states are deliberately **not** shown as failures:

- A draft a quality gate held back (`action.skipped`) is the system working.
  It appears as an `info` item linking to Reach, where `article_rejects`
  shows which gate fires most.
- An evolution proposal on a review branch is `good`, with a "review diff"
  link; it becomes main only when merged.

And one is shown as a warning although `llm_engine.live` is `true`: **Atria
answered 0 of the cycle's calls.** `live` only means Atria was not latched off;
a timeout or empty completion falls through per call without latching, so a
cycle can end "live" with OpenRouter having served everything. `atriaState`
reads `llm_engine.calls` and says "Atria not answering".

## What "Earned" Means

The Overview's earnings tile shows **only money confirmed on-chain** at
`USDT_WALLET_ADDRESS` — `status.wallet.confirmed_usd`, read live from Tronscan
(TRC-20) or Etherscan (ERC-20) each cycle by `bot/status.py:_snapshot_wallet`.

Nothing else may be rendered as revenue:

- Publishing platforms pay nothing, so `bot/earning/articles.py` reports
  `estimated_usd: 0.0`. A non-zero constant there fabricates income — an earlier
  version summed `$0.08` per article into "Total earned" and showed $4.45 that
  did not exist anywhere.
- `earnings.total_usd` / `this_week_usd` are therefore **activity value**, not
  money. Label them as such wherever they appear.
- `code_tech_earning` lead values are **unrealised pipeline**, shown separately.

`wallet.received_total_usd` accumulates observed balance increases above a
high-water mark, so it survives a manual withdrawal without double-counting the
recovery. `wallet.stale` means the chain lookup failed and the last known
balance is being shown; no receipt is recorded for that cycle.

The wallet is a **receive** address printed in every published article's
footer (`bot/earning/payout.py`), so tips arrive already at their destination.
There is no transfer step and no withdrawal code path anywhere in the tree.

Only the masked address (`wallet.address_masked`) is written to tracked files;
`sanitize_for_git` redacts the raw value.

## Visual Rules

- Flat and quiet: no background washes, glows or gradients. Colour carries
  meaning only (status dots, icons, verdict rule), never decoration.
- Tile values are in text ink; the tile's tone shows in its icon and detail.
- Charts are single-series bars (`BarList`): one accent hue on a shared zero,
  the value printed beside each bar, and the sample size as `n=` so a mean over
  two posts reads as one. Rows below `_MIN_ARCHETYPE_SAMPLE` are drawn faint.
- Both themes come from the same tokens; check light and dark, and a 390 px
  phone width, before shipping.

## Implementation Notes

- Keep `status.json` backwards-compatible; every computed property must tolerate
  missing keys. Sections receive the whole snapshot and must not assume presence.
- Keep GitHub Pages static: no backend server. Python writes data, Vite builds
  the browser app, and the browser reads static files.
- Suggestion views prefer code-tech, dev.to, and free LLM work. `isAvoidedSuggestion`
  filters recommendations needing KYC, paid access, phone-gated APIs, or funded
  wallets.
- Suggestion cards render `owner_action` (the evolution brief schema). The
  free/paid pill shows only when `free_tier` is a boolean: the brief schema
  dropped that field, and reading its absence as `false` labelled every new
  owner action "paid".
- When adding a new module or secret, update `bot/status.py` first, then extend
  the relevant section in `frontend/src/sections/`.
- Build with `pnpm build` from `frontend/` so `docs/` holds the public artifacts.
  The prebuild step clears all hashed bundles, because section chunk names are
  open-ended and stale files would otherwise accumulate.
