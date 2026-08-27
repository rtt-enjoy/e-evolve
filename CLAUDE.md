# CLAUDE.md — E-Evolve

## Code Change Rules

1. **Don't assume. Don't hide confusion. Surface tradeoffs.**
2. **Minimum code that solves the problem. Nothing speculative.**
3. **Touch only what you must. Clean up only your own mess.**
4. **Define success criteria. Loop until verified.**

---

## Project Overview

E-Evolve is a GitHub Actions bot that runs hourly and refreshes RAG, market research, and earning suggestions. It also proposes its own code changes: Phase 3 evolution is enabled, but every proposal lands on an `evolve/*` review branch and reaches `main` only when a human merges it. Zero server cost — runs entirely on GitHub Actions free tier.

Current operating policy: API keys are for RAG, research, market analysis, suggestions, draft text, and **publishing articles to dev.to**. The bot must not use keys to post to social media, place trades, mint NFTs, withdraw funds, or comment on external issues.

**Main AI engine: free OpenRouter models via `bot/llm.py`** — no paid engine, no credits required. Every role routes through a zero-cost chain ordered by capability, all led by `minimax/minimax-m3:free` (1M context, $0 in/out, native `response_format` + tools). Each role then diverges by task: `upgrade` falls back to code-specialised models (`poolside/laguna-s-2.1:free`, `cohere/north-mini-code:free`), `research` to the largest-context reasoners (`nvidia/nemotron-3-ultra-550b-a55b:free`, `nvidia/nemotron-3-super-120b-a12b:free`), and `post` to models with native structured output. On 402/429/model-not-found, `bot/llm.py` steps down through *every* remaining model in the role's chain — each getting a fresh retry budget — before falling back to another provider, so a cycle never fails on cost or one model's rate limit.

---

## Architecture

```
bot/main.py          ← 5-phase orchestrator (entry point)
bot/llm.py           ← LLM abstraction (OpenRouter free chain, then Anthropic/Gemini/Cerebras/Groq)
bot/status.py        ← Phase 1: load/save status.json, feature detection, wallet balance
bot/commands.py      ← Phase 2: owner commands (command.txt or GitHub Issues)
bot/evolution.py     ← Phase 3: LLM code proposals → review branch (never main)
bot/earnings.py      ← cumulative earnings tracker + weekly reset
bot/dashboard.py     ← writes docs/index.html + earnings-log.md
bot/git_utils.py     ← git commit helpers + commit_to_branch (review gate)
bot/github_secrets.py ← reads configured secret NAMES only (never values)
bot/tests.py         ← unittest suite: python -m unittest bot.tests
bot/earning/
  articles.py        ← drafts + publishes one dev.to article per day; follows up its own best post
  devto_stats.py     ← reads own dev.to view counts (the reach feedback loop)
  newsletter.py      ← drafts + publishes a weekly dev.to digest of several trending stories
  trending.py        ← finds recent (24h) tech articles from free public feeds
  code_techs.py      ← free-AI earning opportunity queue (research/suggestion only)
  mrr_ideas.py       ← recurring-revenue idea triage (research/suggestion only)
frontend/            ← React + Vite dashboard, built to docs/ by .github/workflows/frontend.yml
.github/workflows/evolve.yml  ← hourly scheduler (never evolved)
config/strategy.json ← tunable strategy parameters
status.json          ← persisted bot state (auto-updated each cycle)
version.txt          ← current bot version (X.Y.Z)
command.txt          ← owner command input
```

---

## Cycle Flow (5 Phases)

```
Phase 0: Init LLM (OpenRouter free-model chain first, then Anthropic > Gemini > Groq)
Phase 1: Status   — load status.json, detect active features from env secrets
Phase 2: Commands — read command.txt + GitHub Issues labelled "bot-command"
Phase 3: Evolution — LLM proposes code changes; applied to a sandbox, verified,
                    then committed to an evolve/* review branch for human merge
Phase 4: Research — refresh free-AI earning queue and MRR idea triage,
                    draft + publish one article, then draft + publish the
                    weekly newsletter digest when due
Phase 5: Update   — save status.json, write dashboard, commit
```

---

## Safety Boundaries (runtime policy — enforced in code, not by the LLM)

Automatic code evolution is **enabled but human-gated**. Phase 3 lets the LLM
propose code changes, but nothing it writes can reach `main` on its own.

The gate, in order:

1. **Off unless enabled.** `evolution.enabled` in `config/strategy.json` must be
   `true`. Missing config means disabled — never the reverse.
2. **Path allowlist.** Writes only under `bot/`, `docs/`, `config/`,
   `requirements.txt`, `version.txt`. `.github/` and `.git/` are refused, and
   `..` traversal is rejected.
3. **Protected files.** `bot/main.py`, `bot/llm.py`, `bot/status.py`,
   `bot/commands.py`, `bot/evolution.py`, and `bot/git_utils.py` can never be
   written — the orchestrator and the sandbox itself are off limits.
4. **Change cap.** At most `MAX_CHANGES` (3) files per cycle. `max_changes` in
   config can lower this but never raise it.
5. **Syntax + import check.** Python is AST-parsed before writing and
   import-checked in a subprocess after. Failures get up to 2 LLM repair
   attempts, then the backup is restored.
6. **Review branch.** Verified changes are committed to
   `evolve/<version>-<utc>` via `git_utils.commit_to_branch`, then reverted on
   the working branch. The workflow pushes the branch but **never merges it**.
   `main` is unchanged until a human merges.

`version.txt` is bumped **on the review branch only**; the running version
changes when you merge, not when the bot proposes.

The engine is the free OpenRouter `upgrade` chain led by `minimax/minimax-m3:free` —
no paid model and no credits, so a cost error can never break a cycle. Paid
Qwen3.8 variants were evaluated and rejected for this reason.

What the bot may still do at runtime:

- **Allowed:** RAG, research, market analysis, suggestions, drafts, and
  publishing articles to dev.to.
- **Blocked:** social posting, trading, minting, payouts, and commenting on
  external issues. These are refused in code, not merely unconfigured.
- Secrets for blocked actions are treated as research context only and never
  activate a feature (see `status.FEATURE_MAP`).
- Secret *values* are never logged or persisted; `status._secret_values()`
  redacts them before write.

---

## Feature Activation

Features activate automatically when their secrets are present in env.

| Feature          | Required Secrets     |
|------------------|----------------------|
| `llm_anthropic`  | `ANTHROPIC_API_KEY`  |
| `llm_gemini`     | `GEMINI_API_KEY`     |
| `llm_openrouter` | `OPENROUTER_API_KEY` |
| `llm_groq`       | `GROQ_API_KEY`       |
| `llm_cerebras`   | `CEREBRAS_API_KEY`   |

`DEV_TO_API_KEY` enables live article publishing to dev.to (one article per day,
capped by `articles.max_articles_per_cycle`). Without it, the articles module
skips silently.

### Article sourcing (bot/earning/trending.py)

Articles are **never** written from a static topic list — that caused dozens of
identical posts on dev.to. Each article starts from a real trending piece:

1. `trending.fetch_candidates()` pulls tech stories from the last 24h via free,
   keyless public feeds: HN front page (Algolia API), TLDR, InfoQ, Lobsters,
   HackerNoon, dev.to, Smashing, GitHub Blog, Medium tag RSS, HackerRank blog.
2. HN items are keyword-screened by `is_technical()` — its front page also
   carries science/culture stories that make bad developer articles. Feed-based
   sources are already topic-scoped and bypass the filter.
3. `_pick_source()` takes the highest-ranked candidate not in
   `status["article_history"]`, so a source is used at most once, ever. If the
   candidate is on a paywalled host (`trending._PAYWALLED_HOSTS`) and its feed
   summary is too thin to write from, `trending.unlock_summary()` fetches the
   full text once via the public `freedium-mirror.cfd` mirror. If the mirror is
   down or returns nothing useful, that candidate is skipped and the next one is
   tried — the mirror is never required for a cycle to succeed.
4. The LLM writes an *improved, original* article on that subject. The system
   prompt forbids rewording and requires added value (working code, tradeoffs,
   failure modes) plus a `## Source` attribution section. It also fixes the
   **voice**: plain-spoken, short sentences, "you"/"I", no hype, no jargon, and a
   skimmable heading structure where each `##` states an outcome, not a topic.
5. Gates run before publishing, in this order:
   - `_strip_fabricated_tables()` — deletes invented spec tables (latency,
     parameter counts, prices) but keeps the surrounding prose. Deterministic,
     so it costs no LLM call.
   - `_fabrication_problems()` — **hard reject.** If invented figures survive in
     prose, publish nothing. Checked *before* `_revise_format()` so a doomed
     article costs one LLM call instead of two.
   - `_title_problems()` — **the reach gate.** A weak headline is why a good
     article gets no views, so the title is checked on its own and, if weak,
     rewritten by a cheap title-only call (`_revise_title`). If the rewrite is
     still weak, **publish nothing** — a title that cannot earn a click makes
     the body irrelevant. Rejects clickbait ("ultimate", "top N", "you need to
     know", "deep dive"), exclamation marks, shouted words, vague filler
     ("getting started", "better code"), colon-subtitle padding, and anything
     outside `title_min_chars`–`title_max_chars`. Real acronyms (JSON, HTTPS,
     SQLite) are allowlisted, so `_shouted_words` does not reject legitimate
     technical headlines.
   - `_format_problems()` — structure + `_tone_problems()` (hype, "simply/just",
     corporate jargon, exclamation marks, sentences averaging over 26 words).
     Only these trigger a revision call. The vetted title is re-applied
     afterwards, because `_revise_format` tends to echo the pre-gate one.
   - `_boost_tags()` — tags are how dev.to distributes a post, so a post tagged
     only with niche slugs reaches nobody. Guarantees at least one high-traffic
     tag, preferring one proven on this account (`article_stats.winning_tags`)
     over the static default.
   - `_too_similar_to_source()`, `_duplicate_reason()`, `_ensure_attribution()`.

**If no fresh source is found or the LLM fails, the bot publishes nothing.**
There is deliberately no fallback article — a static fallback is what produced
the duplicate flood. Title matching is stemmed and stopword-stripped
(`trending.normalize_title`) so "Costs"/"Cost" and "Under"/"During" variants
cannot slip a repeat through.

### Reach feedback loop (bot/earning/devto_stats.py)

Views were low partly because the bot never looked at its own numbers — every
post was a blind guess. `devto_stats` closes that loop by reading
`GET /api/articles/me/published`, which returns `page_views_count`,
`positive_reactions_count`, and `comments_count` for the key's own articles.

- Read-only, and it reuses `DEV_TO_API_KEY`. **No new secret.**
- `engagement_score()` weights a reaction at 25 views and a comment at 50. Raw
  views alone rank a single lucky aggregator link above a post that genuinely
  landed, which is the wrong thing to imitate.
- `summarize()` writes `status["article_stats"]` (count, total/avg views, best
  post) so reach is visible in `status.json` instead of invisible.
- `winning_tags()` averages engagement per tag rather than summing it, so a tag
  used once on a hit is not buried by a tag used twenty times on quiet posts.
- Every function returns empty/None on failure. Stats are an optimisation: a
  dev.to outage must never stop the day's article.

**Follow-up articles.** When a recent post has earned real attention,
the next article is a *deeper sequel* to it rather than a cold trending guess:

1. `_followup_target()` picks the best post within `followup_window_hours` (48)
   that cleared `followup_min_views` (40) and has not been followed up before.
2. `_generate_followup()` writes it under `_FOLLOWUP_SYSTEM` — `_SYSTEM` plus
   follow-up rules: recap the first post in at most two sentences, then add the
   depth it lacked (production edge cases, what is harder than it looks, what
   you'd do differently). Re-explaining the basics is explicitly forbidden.
3. `_titles_overlap()` discards a sequel whose title merely repeats the parent's.
4. `_ensure_backlink()` inserts the link to the parent after the opening
   paragraph — as context, not a trailing footnote — if the model dropped it.
5. The parent's id is recorded in `article_history.followed_up_ids`, so the same
   winner is not mined again while it remains the top performer.

A **new post** is published rather than editing the original in place: dev.to
does not re-surface edited posts in the feed, so an in-place edit gains almost
no new readers. Two live posts both rank, and the backlink sends the sequel's
readers to the original.

Both paths share one gate pipeline (`_finalize`), so the fresh and follow-up
articles cannot drift apart on fabrication, tone, title quality, or duplicates.
A failed follow-up falls through to the normal trending path — it never costs
the day's article.

### Newsletter digest (bot/earning/newsletter.py)

A weekly "what shipped in tech" digest published to dev.to. Where `articles`
writes one deep piece about a single source, the newsletter writes one short
section about each of several sources. Same secret (`DEV_TO_API_KEY`), same
policy, same house style — it is a second product, not a second channel.

- Sources come from the same `trending.fetch_candidates()`, with
  `source_max_age_hours: 168` so a weekly issue sees the whole week.
- `_pick_sources()` takes the top `items_per_issue` (7) candidates not already in
  `status["newsletter_history"]`. A story is featured **at most once, ever**.
- If fewer than `min_items` (4) fresh stories survive, **it publishes nothing** —
  and returns before calling the LLM, so a dead week costs zero free-tier requests.
- **One LLM call per issue**, not one per story. This matters against the
  OpenRouter free-tier daily ceiling.
- It does *not* call `trending.unlock_summary()`; a digest paragraph does not
  need full paywalled text, and skipping it avoids ~7 extra HTTP fetches.
- Gates reuse `articles`' `_normalize`, `_strip_fabricated_tables`,
  `_fabrication_problems`, and `_tone_problems`, so the two modules cannot drift
  apart on fabrication or voice. Structural checks are local
  (`_digest_problems`), because `articles._format_problems` asserts essay rules
  (2+ code blocks, `## Key Takeaways`) a digest legitimately lacks.
- A dropped source link is repaired deterministically by `_ensure_sources()`
  rather than rejecting the whole issue; anything else fails the issue.
- Cadence is self-managed via `newsletter_daily.published_at` against
  `min_interval_hours` (168). The hourly pulse therefore yields one issue a week.
- History is deliberately **separate** from `article_history`: a story may be
  both a digest paragraph and, later, a full article.

Newsletter history and cadence live in `status["newsletter_history"]` and
`status["newsletter_daily"]`. Both are bounded by `history_limit`.

> **Not implemented, on purpose.** The source article that prompted this feature
> described three "autopilot income" systems. Systems 2 (auto-posting affiliate
> content to social platforms) and 3 (scraping leads and auto-sending cold email)
> were **rejected**: both require actions this project blocks in code, and
> widening those boundaries needs an explicit owner decision. Only the newsletter
> was built, and it publishes to dev.to — a channel already allowed.

### MRR idea triage (bot/earning/mrr_ideas.py)

A recurring-revenue reality check. It scores business models against this
project's real constraints — zero server, no payment processing, no inbound
HTTP, no outreach channel — and writes `docs/mrr-ideas.md` with the few that
survive plus, explicitly, the ones it refuses and why.

- Suggestion-only. It never contacts anyone, processes a payment, or hosts a
  service. No new secret; it gates on `mrr_ideas.enabled` in strategy config.
- The triage is **deterministic** (`_triage` against `_BLOCKERS`), so refusals
  cost no LLM call and cannot be argued away by a model.
- The line is drawn at **delivery, not billing.** Every recurring-revenue model
  needs a way to charge — that is what MRR means — and the owner can open a
  Gumroad or Substack account by hand. So `payments` is a `_MANUAL_STEPS`
  prerequisite, not a blocker. Treating it as a blocker refused all 20 ideas and
  made the report useless; that was caught and fixed during implementation.
- **One LLM call per refresh**, and `refresh_hours: 48`, so the module costs
  about 0.5 free-tier requests a day. Every cheap gate — disabled, interval not
  due, nothing viable, no LLM client — returns before that call.
- A dead or failing LLM degrades to the deterministic triage rather than
  erroring: the refusal record is the useful half and it still gets written.
- State lives in `status["mrr_ideas"]` / `status["mrr_ideas_history"]`, bounded
  by `history_limit`.

> **Not implemented, on purpose.** The source article ("Top 20 Side Hustle
> Projects That Will Generate MRR in 2026") lists twenty models. Eighteen do not
> survive this stack's constraints, and the module records each refusal rather
> than pretending otherwise:
>
> - **Blocked by policy (7):** local-business AI automation agency, social media
>   management, SEO retainer, email marketing management, paid Discord/Slack
>   community, YouTube automation, and content repurposing. Every one needs cold
>   outreach to acquire a client or social posting to deliver, and both are
>   refused in code. This is the same decision already recorded for the
>   newsletter's source article; widening those boundaries needs an explicit
>   owner decision.
> - **Impossible on this infrastructure (9):** micro SaaS, bookkeeping, podcast
>   production, white-label SaaS reselling, no-code app dev, tutoring/coaching,
>   virtual assistant agency, a niche API/data feed, and a niche job board.
>   These need a human delivering a service, a paid platform, inbound HTTP, or a
>   credential the owner lacks. None exists here and none is free.
> - **Below the fit threshold (1):** online course membership — unblocked, but it
>   needs a pre-existing audience plus two manual setup steps, which scores
>   under `min_score`.
>
> The article's own critical first step — "find 10 people with the problem, talk
> to them, charge before building" — is outreach plus payment collection. The bot
> cannot do it, so the report tells the **owner** how to do it through inbound
> channels instead, and says plainly which part no automation here will cover.
>
> A **paid** API/data feed (idea 17) was also not built beyond being refused.
> GitHub Pages can serve static JSON for free, but a paid feed needs auth,
> metering, and billing, and a free feed earns nothing while adding a
> maintenance surface. That tradeoff is the owner's call, not a default.
>
> **This module produces no revenue by itself.** It produces a
> constraint-checked shortlist and a refusal record. With client acquisition and
> payment collection both outside the boundary, that is the ceiling for
> automation here — the article says as much: "none of these will work on
> autopilot in month one."

Social posting, trading, minting, and payout secrets do not activate runtime
actions. If such keys exist, they are treated as research context only.

---

## LLM Client (bot/llm.py)

- Provider priority: `OPENROUTER_API_KEY` → `ANTHROPIC_API_KEY` → `GEMINI_API_KEY` → `CEREBRAS_API_KEY` → `GROQ_API_KEY`
- **Main engine: free OpenRouter models, used for every role in `ROLE_PROVIDER`. No paid model, no credits needed.**
- **OpenRouter free-tier ceiling:** `:free` models are capped at 20 req/min and only
  50 requests/day unless the account has ever bought $10 in credits (then 1,000/day).
  An hourly bot with multiple LLM calls per cycle can approach that ceiling — verify
  the current limit at openrouter.ai/docs before assuming headroom.
- Model chain is role-aware via `_OPENROUTER_MODELS_BY_ROLE`. Every chain leads with
  `minimax/minimax-m3:free` and holds 6 entries, ordered hardest/most-capable first and ending in the
  `openrouter/free` auto-router so there is always a last resort:
  - `upgrade` → code-specialised fallbacks (`poolside/laguna-s-2.1:free`, `cohere/north-mini-code:free`)
  - `research` → largest-context reasoners (`nvidia/nemotron-3-ultra-550b-a55b:free`, `minimax/minimax-m3:free`)
  - `post` → models with native `response_format`, so JSON drafts don't come back wrapped in prose
  - all other roles use the `_OPENROUTER_MODELS` default chain
- **Model availability is not permanent.** `stealth/ox-alpha` led every chain until it was
  withdrawn from OpenRouter; the chains were re-led by `minimax/minimax-m3:free`, chosen by
  probing the live `/api/v1/models` catalogue and test-calling each candidate. No model is ever
  the only entry in a chain; a 404 advances to the next one.
- **Verified-unusable, deliberately absent:** `thinkingmachines/inkling{,-small}:free` is the
  strongest free model on paper (975B MoE, 1M ctx) but returns **HTTP 403 — "only available on
  agentic harnesses"**, so this bot cannot call it. `dots-studio/dots-3-note-preview:free` and
  `nvidia/nemotron-3.5-lightning:free` failed to return parseable JSON. Re-probe before adding
  any of them back.
- Stepping down the model chain does **not** consume the 3-attempt retry budget — each model gets its
  own. (Before this was fixed, a 5-model chain gave up after 3 models.)
- On 429 or model-not-found, the OpenRouter call steps down through the rest of the
  role's free-model chain before abandoning the provider — a rate limit degrades
  quality (smaller/different free model), never breaks the cycle.
- `CEREBRAS_API_KEY` is an optional extra free-tier fallback (roughly 1M tokens/day,
  14,400 requests/day per model, no credit card) used when OpenRouter/Anthropic/Gemini
  are unavailable or exhausted. See `bot/llm.py` `_call_cerebras` / `_CEREBRAS_MODELS`.
- To change the default engine, edit `_OPENROUTER_MODELS` (and the per-role lists) in `bot/llm.py`
- Anthropic default model: `claude-sonnet-4-6` (fallback chain)
- All calls retry 3× with exponential backoff
- `complete_json()` appends JSON-only instruction and strips markdown fences

---

## Owner Commands

Write to `command.txt`, commit. Next cycle executes and clears them.
Also works via GitHub Issues with label `bot-command`.

```
force articles N         # publish N articles now, bypassing the daily cap (max 5)
force newsletter         # publish a newsletter digest now, bypassing the weekly cadence
force mrr                # refresh the MRR idea triage now, bypassing the interval
force trade aggressive   # ignored: trading is disabled
force mint N             # ignored: minting is disabled
skip evolution           # skip Phase 3 evolution for this cycle
improve suggestion TEXT  # focus this cycle's evolution on that suggestion
reset earnings           # zero this_week_usd
post thread              # ignored: social posting is disabled
status report            # dump full status to workflow log
```

---

## State Schema (status.json)

```json
{
  "version": "X.Y.Z",
  "last_run": "ISO datetime",
  "total_runs": 0,
  "active_features": [],
  "inactive_features": [],
  "llm_provider": "groq|anthropic",
  "earnings": {
    "total_usd": 0.0,
    "this_week_usd": 0.0,
    "last_cycle_usd": 0.0,
    "week_started": null,
    "breakdown": {}
  },
  "last_evolution": { "summary": "", "changes_applied": [], "suggestions": [] },
  "last_earning": { "actions": [], "total_usd": 0.0 },
  "suggestions": [],
  "errors": []
}
```

Keys prefixed `_` are runtime-only and not persisted.

Earning modules own their own sub-trees alongside the above: `article_daily` /
`article_history` / `article_stats` (articles), `newsletter_daily` / `newsletter_history`
(newsletter), `code_tech_earning` (code_techs), and `mrr_ideas` /
`mrr_ideas_history` (mrr_ideas). Every list stored in these is bounded by the
module's `history_limit` so `status.json` cannot grow without end.

---

## Strategy Config (config/strategy.json)

Tunable by owner or changed here in Codex:

```json
{
  "articles":       { "max_articles_per_cycle": 1, "min_interval_hours": 6,
                      "source_max_age_hours": 24, "history_limit": 200, "min_words": 700,
                      "followup_enabled": true, "followup_window_hours": 48,
                      "followup_min_views": 40,
                      "title_min_chars": 25, "title_max_chars": 70 },
  "newsletter":     { "enabled": true, "min_interval_hours": 168, "items_per_issue": 7,
                      "min_items": 4, "source_max_age_hours": 168,
                      "history_limit": 200, "min_words": 500, "niche_focus": "" },
  "mrr_ideas":      { "enabled": true, "refresh_hours": 48, "max_ideas": 8,
                      "min_score": 50, "history_limit": 100 },
  "code_techs":     { "enabled": true, "refresh_hours": 24, "max_items": 8,
                      "min_score": 55, "auto_pursue": false, "...": "searches, sources, outreach" },
  "evolution":      { "enabled": true, "branch_prefix": "evolve", "max_changes": 3 },
  "llm":            { "main_engine": "minimax/minimax-m3:free", "provider": "openrouter" },
  "research_policy":{ "allowed_actions": ["research", "suggestions", "drafts", "article publishing"],
                      "blocked_actions": ["social posting", "trading", "minting", "payouts"] }
}
```

---

## Versioning

- Patch bump: bug fixes
- Minor bump: new features
- Major bump: rewrites
- LLM proposes version in evolution response; rejected if not `X.Y.Z` format — auto-bumps patch instead

---

## Commit Convention

Prompt-driven repository changes must be committed and pushed before ending the
prompt whenever verification succeeds and the worktree has changes.

- Use Conventional Commit headers that satisfy commitlint defaults:
  `<type>(<scope>): <subject>`.
- Keep the header at 72 characters or less.
- Use lower-case types from the default commitlint set: `build`, `chore`, `ci`,
  `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`.
- Keep the subject non-empty, lower-case where natural, and without a trailing
  period.
- If there are no file changes, do not create an empty commit.
- After committing, push the current branch to `origin`.

Examples for prompt-driven changes:

```
docs: document prompt commit workflow
fix(earning): handle empty article topics
```

Bot-generated cycle commits keep their existing operational format:

```
🧬 evolve vX.Y.Z: <summary>    ← evolution changes
📊 cycle #N +$X.XXXX Xs         ← state update each cycle
```

---

## Local Development

```bash
# Create .env with keys
cp .env.example .env   # if it exists, else create manually

# Install deps
pip install -r requirements.txt

# Run one cycle
python -m bot.main
```

---

## What Not to Do

- Never modify `.github/workflows/evolve.yml` unless explicitly asked — it is the heartbeat
- Never add secrets to code or logs
- Never widen evolution safety boundaries without explicit owner decision
- Never add speculative features (new earning modules, retry logic for impossible edge cases)
- Never mock external APIs in earning modules — failures surface as action errors, not crashes

---

## Bug Fixing Workflow

- Use `EVOLUTION_TODO.md` as the execution contract: resolve items in priority order, then update the file itself.
- Before fixing any bug, state the root cause hypothesis and which file/line. Do not edit until the diagnosis is stated.
- After multi-file changes, run `python -m py_compile bot/*.py bot/earning/*.py` and verify no import errors before declaring done.
- Never declare a fix complete without running one local cycle (`python -m bot.main`) or confirming the specific assertion that was failing now passes.

---

## Dashboard (docs/index.html)

- CSS variables are defined in the `:root` block at the top of the file. Never hardcode hex values — use `var(--ac)`, `var(--gn)`, `var(--rd)`, etc.
- `dashboard.py` regenerates `docs/index.html` each cycle from `status.json`. Changes to the HTML template must be made in `bot/dashboard.py`, not in `docs/index.html` directly (they will be overwritten).
