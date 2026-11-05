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

There is no raw-data route: `#/data` was removed 2026-11-05 (see Section
Registry).

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

And one is shown as a warning although `llm_engine.live` is `true`: **the main
engine (GLM) answered 0 of the cycle's calls.** `live` only means the engine was
not latched off; a timeout or empty completion falls through per call without
latching, so a cycle can end "live" with a fallback having served everything.
`engineState()` (`utils/engine.ts`) reads `llm_engine.calls` and says "GLM not
answering".

## Engine page

Top to bottom, each block answers one question and nothing repeats another page:

| Block | Answers | Source |
|-------|---------|--------|
| **Hero** (one card) | Which model writes for the bot, is it serving, and what is the fallback order? A ~20px model name, a state pill, one detail line, then the two chain steps side by side (GLM, then Atria, with calls served). A yellow line appears only when `main_model` is not `preferred_model`, with the refusal from `llm_engine.refused`. | `llm_engine`, `engineChain()` |
| **Roles** and **Engine facts** (balanced pair) | Which model answered each job; is the key set, which host, who is the fallback and why, how many calls each engine answered. Role rows show the model that *answered*, never `llm_workflows.<role>.model`, which is only the preference. | `llm_workflows`, `llm_engine` |
| **Evolution proposal** | What did the last evolution decide? A 3-line clamped summary and a status pill (`in review` / `no proposal` / `failed`), or the *review diff* link. | `last_evolution` |
| **Owner actions** | What only the owner can do. One ~40px row per suggestion. | `last_evolution.suggestions` |
| **Cycle actions** | What the research phase emitted. **Not rendered when empty.** | `last_earning.actions` |

**Proposal and prompt are click-to-open.** Both are long, free-form model text
(the live proposal summary alone is ~1,000 characters), so they sit behind the
`Fold` row (`components/ui.tsx`) instead of stretching the page:

- *Proposal details* opens **Summary** (full), **Serves**, **Money path**, **How
  to verify**, **Evidence** (bullets), **Files changed** (file and reason) and
  **Branch**, each a small uppercase label over a paragraph. A part with no data
  is omitted, not shown as a dash. The same fields are written to the review
  branch's commit body, so the page and the branch tell one story.
- Each owner action opens **Why**, **You do**, **Steps** (numbered; a leading
  `Step N:` written by the model is stripped so numbering is not doubled) and
  **Prompt**: the text `suggestionPrompt()` builds from the fields the bot
  wrote, in a scrollable `code-block` with a `copy prompt` button. The prompt
  contains nothing the bot did not write.
- There is no field for the *evolution engine's own* prompt in `status.json`
  (`last_evolution` stores only the rationale), so none is shown. Adding one is
  a backend change and an owner decision, not a UI tweak.

Removed from this page (2026-11-05): the **Raw role map** (it restated Roles;
`llm_roles` is no longer claimed by the registry) and the Cycle / Last run /
Duration rows (Health owns run facts).

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

## Design Principles

These hold for every page. The 2026-11-03 rule ("generous spacing, `py-4` or
more") was superseded: Leads, Health and Engine were each found needlessly large
and were compacted. **Compact is the default; generous spacing is the exception.**

**Look**

- Flat and quiet: no background washes, glows or gradients. Colour carries
  meaning only (status dots, icons, verdict rule), never decoration.
- Colours are RGB-triplet tokens in the `:root` block of `styles.css`; never a
  hex value. Both themes come from the same tokens; check light, dark and a
  390 px phone before shipping.
- Tile values are in text ink; the tile's tone shows in its icon and detail.
- Charts are single-series bars (`BarList`): one accent hue on a shared zero,
  the value printed beside each bar, the sample size as `n=` so a mean over two
  posts reads as one. Rows below `_MIN_ARCHETYPE_SAMPLE` are drawn faint.

**Size** (what "right-sized" means, measured)

| Element | Size |
|---------|------|
| List / secret / role row | ~36-44px, `py-2` to `py-2.5` (Leads rows have two lines, ~75px, never below `py-3.5`; the list is grouped and paged, see 2026-11-05) |
| Module chip | ~32px |
| Fold summary row | ~40px |
| Card | `card-compact`: `gap-4`, `p-4 sm:p-5` (default `.card` is `gap-5`, `p-5 sm:p-7`) |
| Secondary text | 12.5-13.5px, `leading-snug` to `leading-[1.65]` |
| Hero model name | 19-21px (it was 26-32px; a name is not a headline number) |
| Pills in rows | `px-2 py-0 text-[11.5px] leading-5` |

**Structure**

1. **Summary visible, detail one click away.** Anything long or free-form (a
   proposal, a prompt, a lead's reasoning) shows a clamped line or a title and
   opens on click: `Fold` for a row, `Disclosure` for a whole block. Do not
   render model prose in a `KeyValue` cell; it makes the card as tall as the text.
2. **Hide what is empty.** A card with nothing to say is not rendered (Cycle
   actions, Owner actions). A part of a detail view with no data is omitted.
   An empty-state card is for a page whose *purpose* is empty, not a sub-block.
3. **One owner per fact.** Run facts (last run, duration, cycle) live on Health;
   the funnel on Overview; the model that answered on Engine. A second copy
   drifts, and a second place to look makes a worse page. If another page needs
   the fact, link to its owner.
4. **Balanced columns.** Side-by-side cards use `split even` and should be of
   comparable height (fill the shorter with content that belongs there, never
   filler). A chain of two steps uses two columns, not three with a dead slot.
5. **Show the observation, not the preference.** A label reads what the cycle
   did (`llm_engine`, `receipt_check`, `wallet`), never what config says should
   happen. See Staying In Sync and What "Earned" Means.
6. **Scope every compact modifier to its page.** Add `card-compact`, `rowlist`,
   `*.compact`, `stack.tight`, `split.even` or a page-named class; never edit a
   shared class (`.card`, `.suggestion`, `.disclosure`, `.keyvalue`) to tighten
   one page. `.suggestion` is shared with Research and Leads.
7. **Dense is not cramped.** Cards keep a gap between header and body; leave
   `.segmented` at `p-1.5` / `gap-1` (set 2026-11-03 so the active chip is not
   2 px from the frame).
8. **One state per colour.** `good` = working, `warn` = degraded but serving,
   `bad` = broken, `info` = awaiting a human (review branch), `neutral` =
   unknown or idle. A held-back draft is `info`, never `bad`.
9. **Names are real.** `featureLabel` upper-cases `GLM`, `USDT`, `MRR`, `CTF`,
   `API`, `LLM`; do not hand-format an acronym in a component.

**Process rule.** A `frontend/src` change is not live until `pnpm build` has
rebuilt `docs/` and it is committed with the source. `pnpm build` runs
`tsc --noEmit` first, so a type error stops it. Record every UI change below in
the same commit.

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

## 2026-11-05 changes

- **Leads: restructured, not re-padded (owner: "cleaner, compact, and nicer").**
  The earlier 2026-11-05 padding pass left a 4-tile row, two filter rows with one
  chip per subreddit, a flat list of 32 rows with five pills each, and a lower
  block of 12 full-height refused-route cards. What changed:
  - **One stat strip** (`.leads-stats`, ~52px) replaces the four tiles: routes,
    posted in 24h, new this refresh, free to start, needs setup.
  - **Filters are chips** (`.leads-chip`): one search + sort row and one row of
    kind / quick / source chips. Sources group by **feed** (`sourceFamily`:
    `reddit:r/SaaS` and `reddit:r/SideProject` are both Reddit), because every new
    feed would otherwise widen the row. `sourceName` is the one place a feed gets
    its real name.
  - **Two groups, "Gets paid" and "Build & market"** (`.lead-group`), each paged
    at 20 with a `Show N more` button. The curated channels no longer sit
    between the fresh rows, so the daily change is visible at a glance. The
    kind pill is gone (the header says it) and so is the added-ago pill (it stays
    in the detail facts). A row keeps `new`, `free` or a fee, and plain
    `Feed · age` text.
  - **Everything below the list is closed**: Where leads come from, Refused
    routes (one `Fold` each) and the four playbook blocks are `Disclosure`s under
    one `Reference` heading. The refused list was 12 cards taller than its
    neighbour, which broke the balanced-columns rule.
  - **Detail page**: `tile-row compact`, `split even`, `card-compact`; the Codex
    prompt is a closed `Fold` with `copy prompt`; Lead facts drop the rows the
    tiles already show (cost, score, kind, new).
  - Fetched rows show a 140-character excerpt of the post or repository as the
    reason (`_reason`), not one sentence shared by every row.
  Page-scoped classes only: `.leads-*`, `.lead-group*`, `.lead-more`,
  `.lead-row-src`. `.segmented`, `.card` and `.suggestion` are untouched.

- **Leads: compact layout.** The owner found each card needlessly large, and
  asked for compact but not dense. A lead row is now two lines (title, one-line
  reason) with the pills in a right-hand column: ~75px a row instead of ~115px.
  The reason clamps to one line on a desktop and two on a phone, and the full
  text is the hover `title` and sits on the detail page. The tile row, the list
  card and the two lower cards use the `compact` / `card-compact` / `stack.tight`
  modifiers in `styles.css`, scoped to Leads so other pages keep the 2026-11-03
  spacing. Do not tighten rows past `py-3.5`, and leave `.segmented` padding alone.

- **Health: compact layout.** The owner found the Modules and Secret readiness
  items needlessly large. A secret is now one ~36px row (dot, name, missing key,
  `n/m` pill) under a single readiness bar, instead of a bordered ~90px card with
  its own bar. Modules are a 3-column grid of ~32px chips, the inactive one
  dimmed; counts sit in the card header (`card-meta`). Phase results are a
  single-line strip, the Attention queue rows are tighter, Run facts and Receive
  wallet use `KeyValue compact`, and the two columns are balanced (`split even`)
  with the wallet status pill moved into its card header. All of it is scoped
  (`card-compact`, `rowlist`, `module-grid`, `*.compact`), so Overview keeps its
  spacing. `featureLabel` now upper-cases `GLM`, `USDT`, `MRR`, `CTF`, `API` and
  `LLM` (it printed `Glm` and `Usdt Wallet`).

- **Engine: compact layout, proposal and prompt behind a click.** The hero is
  one card with a ~20px model name and the two-step chain in two columns. Roles
  are ~44px rows beside an **Engine facts** card (key, host, fallback, calls per
  engine, bot version), so the pair has equal height. The Evolution proposal
  card shows a 3-line clamp; Summary, Serves, Money path, How to verify,
  Evidence, Files changed and Branch open under **Proposal details**. Each owner
  action is a `Fold` row; opening it shows Why / You do / Steps / **Prompt**
  (scrollable code block and `copy prompt`). Removed: the Raw role map
  (`llm_roles` dropped from the Engine registry keys), the Cycle facts card
  (Health owns it), and the empty Cycle actions card. Cycle actions, when
  present, are one-line rows. New shared `Fold` in `ui.tsx`; new scoped CSS
  (`.fold*`, `.brief*`, `.prompt-box`, `.proposal-summary`, `.actions-list`,
  `.engine-hero.compact`, `.roles`); `.change` and `.action` were deleted with
  their only user. The rules this followed are **Design Principles** above.
- **Docs repaired.** The IA table listed `#/data` (removed today), Required
  Signals named `atriaState` and Atria as main engine (it is `engineState` and
  GLM), and Visual Rules still demanded `py-4` rows. All three were rewritten.
