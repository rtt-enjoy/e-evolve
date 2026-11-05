# Frontend Dashboard Contract

`docs/index.html` is the public GitHub Pages dashboard. It is built from the
React/Vite/Tailwind app in `frontend/`, while `bot/dashboard.py` publishes the
safe data files during Phase 5 of every cycle. The browser keeps itself in
sync with the newest cycle without a reload — see **Staying In Sync** below.

## Deploy Retry

`frontend.yml` deploys with `actions/deploy-pages`. When the repo's Pages
source is "Deploy from a branch", every bot commit to `main` also starts
GitHub's own `pages build and deployment` run, and the two can collide: the
deploy is then refused with `due to in progress deployment` (seen once in 60
runs, 2026-11-03, run 41572809901). The deploy step is therefore tried, waited
90 s on failure, and tried once more. A failure that survives the retry is a
real one. Setting **Settings → Pages → Source** to "GitHub Actions" removes the
second deployer entirely, and is an owner action.

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
`GLM_API_KEY` may be rendered so setup remains actionable, but actual
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
| `#/research` | Which CTF bounties can I enter now? (older research is collapsed.) |
| `#/engine`   | Which model served each role, and what did evolution propose?      |
| `#/health`   | Freshness, integration readiness, errors, receive-wallet state.    |
| `#/data`     | Every snapshot field, including keys no section claims yet.        |

`#/leads/<index>` is a detail view carrying the lead's `codex_prompt` with a
copy button.

**Leads expansion (owner request 2026-11-03: "show more").** The list page now
has:

- A **New this refresh** tile and a `new` pill per row (`lead.is_new`), plus a
  posting-age pill on fetched rows.
- Stackable quick filters — **free to start** (published $0 only; unknown cost
  is not free), **no setup**, **new** — and a "Showing N of M" line.
- **Where leads come from**: `code_tech_earning.source_stats` as fetched /
  ranked / shown per source, so a source returning 0 is visible.
- **Refused routes**: `refused_channels` with the reason each was rejected.
- **Product playbook**: product shapes, monetization patterns, strategy
  playbook and avoid patterns. These moved here from Research's collapsed
  "Strategy and guardrails" block. They describe the product route, and showing
  them twice would let the two copies drift.

The detail page adds **Why it scores this** (each `score_parts` component as
points out of its `_score` weight, with any penalty), **First seen by bot**,
and up to four related leads of the same kind. `SCORE_PARTS` in
`LeadsSection.tsx` restates the Python weights (28/22/20/13/10/7), so update it
if `_score` changes.

Related-lead titles wrap (2026-11-03). They inherited `.reference strong`'s
`truncate`, and on an inline `<strong>` that only applies `nowrap`, so a long
title such as "Ask in the artifact, not only beside it — README, --help
output, and docs footer" ran off the **Other places to get paid** card. The
detail view overrides it with `block whitespace-normal break-words`. The shared
`.reference` rule is unchanged, so Research reference cards are not affected.

**Never adult, piracy or other prohibited content (owner rule, top
priority).** `bot/earning/code_techs.py` drops such rows before they reach
`status.json`. `LeadsSection.tsx` also filters them with `PROHIBITED_RE`, as a
backstop for older snapshots. It filters before indexing, so `#/leads/<n>`
links and the detail page agree.

**Every lead row in the `#/leads` list has its own open-source button** (the
external-link icon at the row's right edge, owner request 2026-11-03). It opens
`lead.url` in a new tab, so the owner does not have to open the detail view
first. Keep it:

- The row is a `<div class="lead-row">` holding two sibling links:
  `.lead-row-link` (to the detail view) and `.lead-row-source` (to the source).
  It must not go back to being one `<a>`, because links cannot nest and the
  source button would have to be dropped.
- Rows without a `url` (the curated `local-playbook` / `channel-table` rows that
  have no page) show no button, never a dead one.
- The detail view keeps its own `open source` button as well.

## Section Registry

`frontend/src/sections/registry.ts` is the mechanism that keeps this dashboard
current as the bot evolves. Each section declares the `status.json` paths it
consumes, and two behaviours follow:

1. A section whose declared paths are all empty is **hidden from the nav**, so
   routes never lead to a blank page.
2. A key no section claims is **not shown anywhere**. The `Data` page, which
   dumped the whole of `status.json` node by node, was removed 2026-11-05: it
   served debugging, not the owner's question of whether the system earns, and
   it laid out internal state (`secret_readiness`, `configured_github_secrets`,
   `errors`) on a public page. `JsonNode`, `unclaimedKeys` and the "N new"
   sidebar badge went with it.

**A new backend field therefore needs a section before readers can see it.**
Add its key to the relevant section's `keys` array and render it.

The sidebar still links `status.json` and the earnings log. Those
files are committed and published whatever the UI does, so removing the page
hides nothing that `docs/status.json` does not already serve.

## Required Signals

The Overview must answer, without scrolling:

- Is the cycle fresh, late, or stalled? (sidebar pill and Health; the fourth
  tile is today's article: published, or pending its morning window.)
- The next open CTF bounties (`ctf_bounty.events`), linked to their own sites.
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
cycle can end "live" with a fallback having served everything. `atriaState`
reads `llm_engine.calls` and says "Atria not answering".

## Engine page

One hero card answers "which model writes for the bot": the model GLM's probe
settled on (`llm_engine.main_model`), its state, and the fallback order
GLM → Atria with what each step served last cycle
(`engineChain`). When `main_model` is not `preferred_model`, a yellow line says
why, from `llm_engine.refused`; a snapshot without `preferred_model` was written
before glm-5.3-flash led and says so. Role rows show the model that answered,
not `llm_workflows.<role>.model`, which is only the preference.

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
- Generous spacing: the owner found Leads and Research cramped (2026-11-03).
  A `.card` is a flex column with `gap-5`, so its children (filters, lists,
  key/value blocks) never touch; don't add `mt-*` to a card's direct child.
  Secondary text is at least 13px with `leading-relaxed`; list rows get `py-4`
  or more, with a gap between a title and its detail line.
- Filter chips (`.segmented`, e.g. *every source*, *local-playbook*) have
  `p-1.5` inside the frame and `gap-1` between chips (2026-11-03). At `p-0.5`
  the active chip sat 2 px from the frame, and a wrapped row had no room at
  the right and bottom edges. Do not tighten it again.
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
- **A `frontend/src` change is not live until the rebuilt `docs/` is committed
  in the same commit.** The public page serves the committed `docs/index.html`
  and `docs/assets/*`. On 2026-11-03 two commits changed `frontend/src` (the
  per-row source button and the spacing pass) without rebuilding `docs/`. The
  live page still loaded `LeadsSection-Qe85-t6i.js` from 2026-10-31, so the
  owner saw both changes as lost. Before pushing a UI change, run `pnpm build`,
  commit `docs/`, and check that `docs/assets/` holds the new code (for
  example, `grep` the built chunk for a new class name).
- **The document scrolls, not `<main>`.** `.main` has no height cap and no
  `overflow`, so `mainRef.current.scrollTo()` did nothing. Until 2026-11-03 a
  detail page's scroll offset carried over to the next page, on every section.
  `App.tsx` now calls `window.scrollTo` on every `section`/`detail` change. The
  browser still restores the old offset on Back. If `<main>` ever becomes its
  own scroll box, move the reset back onto it.
- **The Back button lives in the sticky topbar.** It used to be the first
  element of the Leads detail body, so it scrolled away with the page and the
  reader had no way back short of the sidebar. `App.tsx` now renders it in
  `.topbar` whenever the route has a `detail`, labelled with the section name.
  Any section that adds a detail route gets it for free. Do not put a second
  Back link inside a detail view.

## 2026-11-04 changes

- **Leads: every row says when the bot first listed it.** An `added 3h ago`
  pill (tooltip: the exact time) reads `discovered_at`, which `code_techs`
  already carried over between refreshes. The fetched-row pill that used to say
  `5h ago` now says `posted 5h ago`, so the source's posting time and the bot's
  first sighting cannot be confused.
- **Leads: a free route already at 100 is hidden.** `cost_usd === 0` and
  `score >= 100` means nothing is left to do (today: the wallet ask that is
  already live). It is filtered in `LeadsSection` before indexing, like the
  prohibited-content backstop, so tiles, counts, filters and `#/leads/N` links
  all agree. An unknown cost is not free and is never hidden by this rule.
- **Research: every item says when it was added.** CTF events, MRR ideas
  (ranked, surviving, refused), market themes and bot suggestions carry
  `discovered_at`, stamped by `_shared.stamp_first_seen` and carried over by
  id/name/title from the previous snapshot. Rows written before the stamp show
  no pill until their module's next refresh (MRR every 48h, `force mrr` to
  hurry it); on that first refresh every existing row reads "just now".
- **Engine: each evolution suggestion has a `copy prompt` button.** The text is
  built by `suggestionPrompt()` from the fields the bot wrote (title,
  description, owner action, steps) and nothing else, ready to paste into a
  prompt box.
- **Health and Engine: Cerebras, Groq and OpenRouter are gone.** Their
  features no longer exist in `status.FEATURE_MAP`, so Modules, Secret
  readiness and the Engine fallback chain stop listing them once the next cycle
  rewrites `status.json`. The "Configured secrets" card is read from the repo
  and will keep naming `GROQ_API_KEY` / `OPENROUTER_API_KEY` until the owner
  deletes those secrets in GitHub.
