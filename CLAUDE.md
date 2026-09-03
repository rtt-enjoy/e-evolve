# CLAUDE.md — E-Evolve

## Code Change Rules

1. **Don't assume. Don't hide confusion. Surface tradeoffs.**
2. **Minimum code that solves the problem. Nothing speculative.**
3. **Touch only what you must. Clean up only your own mess.**
4. **Define success criteria. Loop until verified.**

---

## Read Before Evolving: docs/passive-income-doctrine.md

**Every evolution starts by reading [`docs/passive-income-doctrine.md`](docs/passive-income-doctrine.md).**
It is the standing brief for what "evolve" means in this project and it outranks
any local improvement a cycle proposes. It carries the six principles, the
scored channel table (so each cycle stops re-deriving the same list), and the
ordered checklist to work through.

The one-line reason it exists: at cycle #1754 this bot had published 10 articles
to **1,838 real views** and earned **$0.00**, because nothing it published ever
gave a reader a way to pay. Reach and wallet were two working halves with a gap
between them. The load-bearing rules that came out of that:

1. **Reach without a receive path earns a structural zero.** Not a poor
   conversion rate — a zero multiplier. Any change that improves reach must say
   where money enters, or be logged honestly as reach work, not earning work.
2. **Rank channels by what runs unattended**, not by upside: no new secret > no
   owner action > within policy > verifiable on-chain > reuses existing output.
   A small channel that compounds beats a large one that needs the owner to open
   an account.
3. **Never let an estimate stand in for money.** `estimated_usd` stays `0.0` on
   a publish even though posts now carry a tip address. Real revenue is the
   on-chain balance, only ever the on-chain balance. And `$0.00` must say *why*
   — nobody tipped, or no footer shipped — because those need opposite fixes.
4. **Boundaries are the design brief.** Social posting, trading, minting,
   payouts, and cold outreach are refused in code, and that is where every
   "obvious" income idea leads. The wallet footer sat *inside* the boundary,
   needing no permission, for 1,754 cycles. Look there first.

---

## Project Overview

E-Evolve is a GitHub Actions bot that runs hourly and refreshes RAG, market research, and earning suggestions. It also proposes its own code changes: Phase 3 evolution is enabled, but every proposal lands on an `evolve/*` review branch and reaches `main` only when a human merges it. Zero server cost — runs entirely on GitHub Actions free tier.

Current operating policy: API keys are for RAG, research, market analysis, suggestions, draft text, and **publishing articles to dev.to**. The bot must not use keys to post to social media, place trades, mint NFTs, withdraw funds, or comment on external issues.

**Main AI engine: free OpenRouter models via `bot/llm.py`** — no paid engine, no credits required. Every role routes through a zero-cost chain led by **`openrouter/free`**, OpenRouter's *free auto-router*: it selects the best zero-cost model per request and filters for the features the request needs, so no role has to name a model up front and the choice tracks the live catalogue. Behind it sits a named fallback chain ordered by capability, led by `minimax/minimax-m3:free` (1M context, $0 in/out, native `response_format` + tools), for when the router itself is rate-limited. Each role's fallbacks then diverge by task: `upgrade` falls back to code-specialised models (`poolside/laguna-s-2.1:free`, `cohere/north-mini-code:free`), `research` to the largest-context reasoners (`nvidia/nemotron-3-ultra-550b-a55b:free`, `nvidia/nemotron-3-super-120b-a12b:free`), and `post` to models with native structured output. On 402/429/model-not-found, `bot/llm.py` steps down through *every* remaining model in the role's chain — each getting a fresh retry budget — before falling back to another provider, so a cycle never fails on cost or one model's rate limit.

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
bot/earning/         ← products own a run(llm, status); support modules do not
  articles.py        ← [product] one dev.to article per day; follows up its own best post
  newsletter.py      ← [product] a weekly dev.to digest of several trending stories
  code_techs.py      ← [product] free-AI earning opportunity queue (research/suggestion only)
  mrr_ideas.py       ← [product] recurring-revenue idea triage (research/suggestion only)
  _shared.py         ← [support] config loading, cadence, feed parsing — used by all four
  devto.py           ← [support] the dev.to publish call + gates every post passes
  trending.py        ← [support] finds recent tech articles from free public feeds
  devto_stats.py     ← [support] reads own dev.to view counts (the reach feedback loop)
  payout.py          ← [support] the reader→wallet path: validated USDT address in every post
frontend/            ← React + Vite dashboard, built to docs/ by .github/workflows/frontend.yml
.github/workflows/evolve.yml  ← hourly scheduler (never evolved)
config/strategy.json ← tunable strategy parameters (the ONLY file in config/)
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

The engine is the free OpenRouter `upgrade` chain led by the `openrouter/free`
auto-router — no paid model and no credits, so a cost error can never break a
cycle. Paid Qwen3.8 variants were evaluated and rejected for this reason, and
`openrouter/auto` is refused on the same grounds (see below).

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

### Shared earning layer (bot/earning/_shared.py, bot/earning/devto.py)

Earning modules split into **products** (each exports `run(llm, status)` and is
called by the orchestrator) and **support** modules (imported by the products,
no `run`). Two support modules exist to stop the products from drifting apart:

- **`_shared.py`** — `load_config`, `hours_until_due`, `parse_dt`,
  `strip_html`, `xml_text`, `bounded_append`. Every module used to carry its own
  copy of these and **the copies had diverged**: `code_techs` held a `_parse_dt`
  that could not read RFC-822 RSS dates (so Reddit/HN `pubDate` silently
  returned `None`) and a `_strip_html` that stripped tags but left `<script>`
  bodies in place as if they were prose. Consolidation adopted the stronger
  implementation, so this was a bug fix, not only a cleanup.
- **`devto.py`** — the publish call plus the gates every dev.to post passes
  (`normalize`, `strip_fabricated_tables`, `fabrication_problems`,
  `tone_problems`, `strip_code_blocks`). `newsletter` used to import these as
  underscore-prefixed privates from `articles`; they are one product's internals
  no longer, so they are a public API here.

Rules for this layer:

- **Config is read at call time, never at import.** `articles` used to bind
  `_MIN_WORDS`, `_TITLE_MAX_CHARS`, and friends into module constants at import,
  which meant an owner's `config/strategy.json` edit could not take effect
  without a reimport, and a test had to monkeypatch a global to change one
  value. Every module now calls `_config()` per invocation. `_title_problems`
  and `_format_problems` take an optional `cfg` so a caller can inject one.
- **A helper used by two modules belongs in `_shared` or `devto`**, not copied
  into the second one and not imported across products through a private name.
- **Product-specific rules stay in the product.** `articles._format_problems`
  asserts essay structure; `newsletter._digest_problems` asserts digest
  structure. Those must not be merged.
- `articles.min_interval_hours` in `config/strategy.json` is **not read**:
  articles gate on the calendar date (one per UTC day), not an elapsed interval.

### Article sourcing (bot/earning/trending.py)

Articles are **never** written from a static topic list — that caused dozens of
identical posts on dev.to. Each article starts from a real trending piece:

1. `trending.fetch_candidates()` pulls tech stories from the last 24h via free,
   keyless public feeds: HN front page (Algolia API), TLDR, InfoQ, Lobsters,
   HackerNoon, dev.to, Smashing, GitHub Blog, Medium tag RSS, HackerRank blog,
   plus named engineering blogs whose masthead a developer recognises —
   Cloudflare, Netflix Tech, Stack Overflow, Martin Fowler, AWS Architecture,
   Google Cloud, GitLab, the Go/Rust/Python release blogs, Chrome for
   Developers, and Mozilla Hacks.
2. **Sources are ranked by editorial authority** (`trending._AUTHORITY`), not by
   recency alone. Every feed item used to score a flat `20`, which left ~26 of
   40 candidates tied and made recency the only tiebreak — so a random Medium
   tag-feed post ranked level with InfoQ, and the bot wrote articles from
   sources nobody has heard of (`kibotronics.net`, a 1978 essay on "solid state
   intelligence"). `_feed_score()` now returns authority + a small recency
   bonus. Medium tag feeds are open-submission and capped at
   `_MEDIUM_AUTHORITY` so they can never outrank an edited publication.
3. Open-submission sources — HN, HackerNoon, dev.to, and every Medium tag — pass
   three independent screens; curated single-publisher feeds are edited, so
   their scoping is trusted. The screens are separate on purpose: each catches
   something the others provably cannot.
   - `is_technical()` — **vocabulary.** The title has to carry a technical term
     on its own; an untechnical title is only rescued by a technical summary.
     This used to pour title and summary into one bag of words and accept a
     single hit anywhere, so one incidental word in a marketing blurb
     whitelisted the post. That is how **"Family Matching Outfits: How to
     Create Stylish Looks for Every Family Member"** — a dev.to clothing-store
     advert — was published as a story in a weekly developer digest, on a
     summary that happened to say "build" and "data".
   - `is_spam()` — **intent.** Vocabulary cannot catch promotional content:
     "MATLAB Online Training | MATLAB Training Courses Online" is full of real
     technical words. Rejects affiliate/listicle spam ("13 Reliable Platforms
     to Buy Gmail Accounts"), agency and course marketing ("Content Marketing
     Services in Noida", "Best PPC and SEO Company in Noida"), roundup padding
     ("100+ ChatGPT Prompts … The Ultimate Collection", "X vs Y vs Z"), and
     feeds in scripts this audience does not read.
   - `is_off_topic()` — **subject.** For posts that are neither keyword-poor nor
     overtly selling: clothing, diet, astrology, visas, and gambling fronts.
     "Shree Win Game Online" cleared the summary rule on a single mention of
     "security" in otherwise pure ad copy.

   **Tightening these is bounded by a false-negative cost.** Demoting generic
   terms (`ai`, `model`, `release`) to weak signals was tried and **reverted**:
   it dropped "Gemini 3.8 Flash", "Quasar 438B" and "Polars 2.0" off Hacker
   News — exactly the stories this bot exists to write about. An empty candidate
   pool is a worse failure than a mediocre source, so when a screen and a real
   article conflict, the article wins and the vocabulary gets the missing word.
4. **The bot's own posts are excluded** (`fetch_candidates(exclude_authors=…)`).
   One of the feeds is dev.to's programming tag, which is also where this bot
   publishes, so its own articles came back as "trending news" a day later. It
   wrote a take on its own top post and credited itself in a `## Source`
   section as though it were someone else's reporting. Following up on our own
   work is a real feature — `_generate_followup`, which recaps honestly and
   backlinks the parent — and this path must not counterfeit it. The account's
   URLs come from `devto_stats.account_urls()` (the dev.to API the stats loop
   already calls), are cached in `article_history.own_urls`, and are read by
   both products through `devto.own_post_urls()`: one account, one list, **no
   new secret and no hardcoded handle**, so it survives a rename.
5. `_pick_source()` takes the highest-ranked candidate not in
   `status["article_history"]`, so a source is used at most once, ever. If the
   candidate is on a paywalled host (`trending._PAYWALLED_HOSTS`) and its feed
   summary is too thin to write from, `trending.unlock_summary()` fetches the
   full text once via the public `freedium-mirror.cfd` mirror. If the mirror is
   down or returns nothing useful, that candidate is skipped and the next one is
   tried — the mirror is never required for a cycle to succeed.
6. The LLM writes an *improved, original* article on that subject. The system
   prompt forbids rewording and requires added value (working code, tradeoffs,
   failure modes) plus a `## Source` attribution section. It also fixes the
   **voice**: plain-spoken, short sentences, "you"/"I", no hype, no jargon, and a
   skimmable heading structure where each `##` states an outcome, not a topic.
7. Gates run before publishing, in this order:
   - `_strip_fabricated_tables()` — deletes invented spec tables (latency,
     parameter counts, prices) but keeps the surrounding prose. Deterministic,
     so it costs no LLM call.
   - `_fabrication_problems()` — **hard reject.** If invented figures survive in
     prose, publish nothing. Checked *before* `_revise_format()` so a doomed
     article costs one LLM call instead of two. It polices four claims:
     latency, pricing, throughput, and benchmark deltas.
     **Model parameter counts are deliberately not among them.** A rule matching
     bare sizes (`7B`, `70B`) was removed after it blocked two of three drafts on
     an LLM-hardware source while their prose was correct — "a 7B model in 4-bit
     sits around 4 GB" is standard notation quoting a published model, not an
     invented spec. That false rejection is why nothing published on 2026-09-01.
     Narrowing it was tried and abandoned: no regex over neighbouring words can
     tell a real model's size from a made-up one, and every attempt either kept
     rejecting correct prose or collapsed into a check that could never fire.
     The writing prompt still forbids fabricated parameter counts.
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

**Why a cycle published nothing (`status["article_rejects"]`).** `_generate_article`
has nine distinct failure exits, and every one used to return a bare `None`.
`run()` then reported all nine as *"no fresh trending source or LLM output
available"* — a message naming **sourcing**, which is usually not the cause. A
live check during a failing cycle found 40 fresh candidates and 0 duplicates
while that string was being written, so the one number the owner could see
pointed at the wrong stage.

Each exit now calls `_reject(code)`, and `_record_reject` persists both
`last_reason` and a running `counts` tally. The tally is the useful half: a
single reason says what happened today, while the counts say *which gate is
actually costing articles* — without them, a gate that quietly kills one draft
in three looks identical to one that has never fired. Codes: `no_llm`,
`no_source`, `llm_error`, `empty_draft`, `fabricated`, `weak_title`,
`revision_fabricated`, `duplicate`, `too_similar`.

`dashboard.write_log` was the other half of the same blind spot: its fallback
branch printed `"action recorded"` and discarded the action's `error`, which is
why 17 dev.to failures in `earnings-log.md` are indistinguishable from each
other. Failed actions now log their reason.

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

**Which articles readers actually want (`interest_report`).** Tags were the only
feedback this loop produced, and on a young account they are close to noise —
one post that happened to land sets the "winning" tags for everything after it.
What predicts engagement is the *kind* of article, so `classify()` buckets each
post into an archetype (`problem-workaround`, `myth-correction`,
`surprising-behavior`, `build-tutorial`, `engineering-culture`,
`security-privacy`) and `interest_report()` ranks the archetypes by **mean**
engagement, reporting `count` alongside so an n=1 fluke is visible as one.

On the real account this immediately showed that `problem-workaround` earns
roughly 25x the engagement of `build-tutorial` — and `build-tutorial` was the
most common thing the bot published. That finding is the point of the feature.

The result feeds two places, and only once it is trustworthy:

- `articles._prefer_proven_archetypes()` re-ranks candidate sources. The
  archetype match is a **bounded bonus on top of** the authority score
  (`_ARCHETYPE_BONUS`), never a replacement for it. Sorting by archetype alone
  let a score-26 Medium post outrank a score-63 InfoQ story purely because its
  title contained "stop" — caught in end-to-end testing and fixed.
- `articles._audience_guidance()` appends the measured evidence to the writing
  prompt, so the article's angle and title are shaped by it. The prompt
  explicitly forbids mentioning the account or its statistics in the article.

`preferred_archetypes()` returns `[]` — no steering at all — until the account
has at least `_MIN_CONFIDENT_SAMPLE` (6) posts **and** some archetype has
actually earned engagement. Steering on an all-zero history would just entrench
whatever happened to be published first.

`status["article_interest"]` holds the report. Stats now refresh on **every**
path via `articles._refresh_stats()`, not just the follow-up path: the guards
for `followup_enabled` and `skip followup` used to return before the fetch, so
turning follow-ups off silently froze the reach data the fresh path depends on.

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

### Reader → wallet path (bot/earning/payout.py)

The link that was missing for 1,754 cycles. See
[`docs/passive-income-doctrine.md`](docs/passive-income-doctrine.md) for the full
reasoning; the mechanics:

Every published post gains a short `## Support this work` footer carrying the
project's validated USDT receive address. It is attached inside
`devto.publish`, so **both products carry it from one call site** and a future
third product cannot ship without it — the same rule that put the dev.to gates
in `devto.py`.

Policy: this is not social posting, trading, minting, or a payout. It adds text
to an article, and article publishing is explicitly allowed. The bot never sends
funds and never touches a key — `USDT_WALLET_ADDRESS` is a *receive* address and
reading it is all the module does. **No new secret.**

- **Deterministic, never an LLM call.** A model asked to write a payment footer
  can transpose a character, and USDT sent to a transposed address is burned.
  Determinism here is a correctness requirement, not a cost saving.
- **Checksum validation, not shape validation.** A regex on
  `^T[1-9A-HJ-NP-Za-km-z]{33}$` accepts an address with two characters swapped,
  and that address belongs to nobody. `valid_tron_address` verifies the
  base58check double-SHA256; `valid_eth_address` verifies EIP-55 when the
  address is mixed-case.
- **EIP-55 needs original Keccak-256, and `hashlib.sha3_256` is not it.** NIST
  changed the padding byte between Keccak's submission and the SHA-3 standard,
  so a check built on the stdlib rejects *every* valid checksummed address. That
  bug was written here first and caught by the EIP's own four test vectors
  before it shipped. `payout.keccak256` implements the real thing in ~40 lines
  rather than adding `pycryptodome` to every Actions run for one address format
  the owner does not currently use. `test_keccak_differs_from_stdlib_sha3` exists
  to stop someone "simplifying" it back into the bug.
- **A malformed address publishes no footer.** A post without a footer earns
  nothing; a post with a broken address costs a reader real money. Not
  symmetric, so the failure mode is always *omit*, logged with a masked address.
- **Attached after every quality gate, deliberately.** The footer adds a heading
  and an untagged fence, which would trip `articles._format_problems` and pad
  the word count enough to carry a too-thin draft past `min_words`. Gates judge
  what the model wrote. `TestPayoutRunsAfterQualityGates` pins this; do not move
  the footer into `_finalize`.
- **`add_footer` never raises and never double-appends.** A footer is an
  enhancement — losing the day's article over it trades real reach for nothing.
- **Off by default** (`payout.enabled: false`). It publishes under the owner's
  byline, so they opt in.
- **No suggested amount.** A figure reads as a price for something already given
  away free, and caps what a generous reader would have sent.

`devto.publish` still reports `estimated_usd: 0.0`, and that is not an oversight.
The tip amount is unknowable at publish time and arrives days later, if at all;
attributing a speculative value to a post because it carries an address would be
the same fabricated-earnings lie this project already deleted once. **Real
revenue is the on-chain balance.**

`status["payout"]` (written by `status._snapshot_payout`) records `enabled`,
`live`, `network`, `address_masked`, and `blocked_reason`. This exists because
`$0.00` because nobody tipped and `$0.00` because no footer ever shipped look
identical in the earnings figures and need opposite responses from the owner.
Only the masked address is ever persisted — `status.json` is committed and the
dashboard is public.

### Newsletter digest (bot/earning/newsletter.py)

A weekly "what shipped in tech" digest published to dev.to. Where `articles`
writes one deep piece about a single source, the newsletter writes one short
section about each of several sources. Same secret (`DEV_TO_API_KEY`), same
policy, same house style — it is a second product, not a second channel.

- Sources come from the same `trending.fetch_candidates()`, with
  `source_max_age_hours: 168` so a weekly issue sees the whole week.
- `_pick_sources()` takes the top `items_per_issue` (7) candidates not already in
  `status["newsletter_history"]`. A story is featured **at most once, ever**, and
  the account's own posts are excluded via `devto.own_post_urls()` like the
  articles path. This product had the worse version of that bug: it features
  seven stories an issue, so a self-post would be presented as one of the week's
  tech news. It also shipped the clothing advert that `is_off_topic()` now
  rejects — a digest paragraph on "Family Matching Outfits" ran as tech news.
- If fewer than `min_items` (4) fresh stories survive, **it publishes nothing** —
  and returns before calling the LLM, so a dead week costs zero free-tier requests.
- **One LLM call per issue**, not one per story. This matters against the
  OpenRouter free-tier daily ceiling.
- It does *not* call `trending.unlock_summary()`; a digest paragraph does not
  need full paywalled text, and skipping it avoids ~7 extra HTTP fetches.
- Gates come from `devto` (`normalize`, `strip_fabricated_tables`,
  `fabrication_problems`, `tone_problems`), so the two modules cannot drift
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
- **`openrouter/auto` is deliberately NOT used.** It is the same auto-routing idea, but its
  candidate set includes **paid** models and it bills at the routed model's rate (the catalogue
  reports its pricing as `-1`, i.e. variable). OpenRouter's docs say it is "built for quality, not
  for staying free" and point zero-cost callers at `openrouter/free` instead. An hourly bot on
  `openrouter/auto` would spend credits every cycle — the exact failure that removed Kimi K3.
  `openrouter/auto-beta` is the same deal. Verified against `/api/v1/models`: `openrouter/auto`
  prices `-1`/`-1`; `openrouter/free` prices `0`/`0`.
- Model chain is role-aware via `_OPENROUTER_MODELS_BY_ROLE`. Every chain leads with the
  `openrouter/free` auto-router (`_MAIN`), followed by `minimax/minimax-m3:free` (`_MAIN_NAMED`)
  and 4 more named free models, ordered hardest/most-capable first. The named tail is not
  redundancy for its own sake — the router is a single upstream service, and a cycle still needs
  somewhere to go when it is rate-limited or degraded:
  - `upgrade` → code-specialised fallbacks (`poolside/laguna-s-2.1:free`, `cohere/north-mini-code:free`)
  - `research` → largest-context reasoners (`nvidia/nemotron-3-ultra-550b-a55b:free`, `minimax/minimax-m3:free`)
  - `post` → models with native `response_format`, so JSON drafts don't come back wrapped in prose
  - all other roles use the `_OPENROUTER_MODELS` default chain
- **Model availability is not permanent** — which is the main argument for the router. `stealth/ox-alpha`
  led every chain until it was withdrawn from OpenRouter, and the chains had to be re-led by hand.
  `openrouter/free` resolves against the live catalogue per request, so a withdrawn model is its
  problem, not a code change here. No model is ever the only entry in a chain; a 404 advances to the next one.
- **The dashboard reads the chain, it does not restate it.** `status.LLM_ROLE_WORKFLOWS`
  is derived from `llm.ROLE_PROVIDER` + `llm._OPENROUTER_MODELS_BY_ROLE` at call time, so the
  Engine panel can never advertise a model the client no longer calls. `bot/status.py` used to
  hardcode the model a second time, which left the UI naming `stealth/ox-alpha` after the chains
  had already moved off it. Only role *purposes* are local to `status.py`.
- **`status.json` is a snapshot, not a source of truth.** The dashboard fetches
  `docs/status.json` at runtime, so a chain change only reaches the UI after the next cycle
  writes it. Changing a model without running a cycle leaves the old name on screen.
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
- **An empty completion is a failure, not an answer.** Every provider routes its
  response through `_require_text`, which raises when a model answers HTTP 200
  with no content. All five API paths used to coerce that to `""` and return
  *successfully*, which broke the chain twice over: `complete()` returned on the
  first model so the 5 named fallbacks were never tried, and `complete_json*`
  then re-sent the same prompt to the same dead model 3x before failing the
  cycle with the misleading `No valid JSON object found ... First 200 chars: ''`.
  That is what skipped evolution on cycle #1751 and produced both `empty_draft`
  article rejects. `_call_claude_cli` already raised on empty output; the API
  paths now match it. An empty response is treated like a 404 — **step down the
  chain**, not retry the same model, because re-asking a model that just
  returned nothing usually returns nothing again and each wasted call comes off
  the 50/day free-tier ceiling.
- **`complete_json*` stops reprompting once every provider is exhausted.** A
  reprompt only helps when a model returned *something* unparseable. When the
  whole chain is dead there is nothing left to ask, so the old 3 full chain
  walks spent 3x the requests to arrive at the same error (18 calls where 6 will
  do). Malformed-but-non-empty output still gets all 3 attempts.
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
force articles N         # publish N articles now, bypassing the daily cap (max 5).
                         # N is honoured: run() loops the publish path N times and
                         # stops at the first failure. It previously read the override
                         # as a bare cap-bypass flag and always published exactly one.
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
`article_history` / `article_stats` / `article_interest` (articles), `newsletter_daily` / `newsletter_history`
(newsletter), `code_tech_earning` (code_techs), and `mrr_ideas` /
`mrr_ideas_history` (mrr_ideas). Every list stored in these is bounded by the
module's `history_limit` so `status.json` cannot grow without end.
`article_history.own_urls` is the account's own dev.to post URLs, refreshed from
the API each cycle by `articles._refresh_stats` and read by **both** products
through `devto.own_post_urls()` so neither can source from itself.

`payout` is written by `status._snapshot_payout` and is not owned by an earning
module — it reports whether the reader→wallet path is live (`enabled`, `live`,
`network`, `address_masked`, `blocked_reason`). It holds only the *masked*
address, because `status.json` is committed and the dashboard is public.

---

## Strategy Config (config/strategy.json)

`config/` holds **exactly one file**, and that is deliberate.
`bot/evolution.py` globs `config/*.json` into the codebase snapshot it sends the
evolution LLM, so anything left in that directory is read by the model as live
configuration. Four stale files were removed for that reason:

- `config/llm_providers.json` and `config/llm_workflows.json` were not valid
  JSON at all — they held Python dict reprs with single quotes, written by
  evolve cycles v1.26.0/v1.28.0 — and described per-role Gemini/Groq routing
  that the all-OpenRouter chain replaced long ago. Nothing ever read them.
- `config/error_handling.json` declared `research_suggestions_only` and blocked
  `publishing`, directly contradicting `strategy.json`'s
  `research_and_article_publishing`. Nothing read it either, but the evolution
  prompt did.
- `bot/utils/` (a `get_env` helper from evolve v1.32.12) was imported by nothing
  and only padded the same snapshot.

Before adding a file under `config/`, make sure something reads it.

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
  "payout":         { "enabled": false, "address_env": "USDT_WALLET_ADDRESS",
                      "heading": "Support this work", "note": "...", "show_network": true },
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
