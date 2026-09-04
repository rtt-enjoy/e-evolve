# Evolution TODO

Bot state: v1.38.0 - cycle #1759 - active: `llm_anthropic`, `llm_gemini`, `llm_openrouter`, `llm_groq`, `articles_devto`, `usdt_wallet`
Receive path: **live** (`payout.enabled: true`, TRC-20) - first receipt still pending.

**Read [`docs/passive-income-doctrine.md`](docs/passive-income-doctrine.md) before
working this list.** It ranks channels by what runs unattended and carries the
scored candidate table, so a cycle does not re-derive the same refused ideas.

---

## Bugs (break current earning)

_(none open)_

---

## High Priority - Earning

- **Publish consistently into the shapes the audience measurably prefers.**
  Doctrine Principle 5, step 3 - and now the *only* remaining earning work that
  does not need an owner decision. The receive path is live on everything
  published, so reach finally compounds into something instead of nothing.
  `status["article_interest"]` measures that `problem-workaround` earns ~25x
  `build-tutorial`, and `_prefer_proven_archetypes` already applies a bounded
  bonus for it. What is not yet known is whether the current bonus is big enough
  to change which source actually gets picked. Measure before tuning: read
  `article_rejects.counts` and the archetype mix of the last ~10 posts first.
  Do **not** widen the bonus into a replacement for the authority score - that
  was tried and reverted, because a score-26 Medium post outranked a score-63
  InfoQ story on the word "stop".

- **Wait for the first receipt before tuning the ask.** `status["attribution"]`
  now records what was live when money arrives, but it has zero receipts, so
  there is nothing to read yet. Per Principle 5, tuning footer wording on a
  sample of zero is noise. When `earnings.received_total_usd` goes non-zero,
  read `attribution.by_archetype` and `by_tag` - and read the `count` beside each
  total before believing the ordering.

---

## High Priority - UI

_(none open)_

---

## Low Priority

_(none open)_

---

## Do Not Touch

- `.github/workflows/evolve.yml` - heartbeat, never evolve
- Research-only policy guards in `bot/main.py`, `bot/commands.py`, and
  `bot/status.py` (FEATURE_MAP) - hardcoded, intentional

---

## Resolved

- **The receive path was built and left switched off for five cycles** - fixed
  2026-09-04. `payout.enabled` shipped `false` on 2026-09-03, which was the
  right default (it publishes under the owner's byline), but nothing turned it
  on. So cycles #1755-#1759 published articles with no ask while
  `status["payout"].live` read `false` and `blocked_reason` said exactly why.
  A structural zero fixed in code and left disabled is indistinguishable, in the
  earnings figures, from never having built it. Enabled by owner decision.
  The doctrine's checklist step 1 and CLAUDE.md now both say to read
  `payout.live`, never "does the module exist".

- **The wallet address is on the public dashboard** - done 2026-09-04. The last
  row of the doctrine's channel table that needed no new secret, no owner
  action, and no policy change. Implemented as `status["payout_public"]`
  (`payout.public_snapshot()`) plus a tip card in `OverviewSection`, reusing the
  existing `CopyButton` and `KeyValue` components.
  Two things are worth remembering. **The full address is required, not the
  masked one** - a tip box built on `TFTNsf…9KbY` renders complete and takes
  nothing, rebuilding the structural zero inside the fix for it; so
  `payout_public` is a separate field from the masked diagnostic and exists only
  when the footer is already publishing that same address. And
  `status._secret_names()` treats any env var containing `WALLET` as a secret,
  so the address was being redacted to `[redacted]` on its way into
  `docs/status.json` - a polished tip box containing the word "redacted",
  failing silently because the page still looked right.
  `status._restore_public_payout` exempts exactly that one field;
  `TestPublicAddressSurvivesRedaction` pins that the exemption stays narrow.
  It went in `bot/status.py` and the React frontend, not `bot/dashboard.py` -
  that module writes `docs/status.json` and the dashboard UI is `frontend/`, so
  the earlier note in this file pointing at `docs/index.html` was wrong.

- **Revenue arrives anonymous** - fixed 2026-09-04, ahead of the first receipt.
  New `bot/earning/attribution.py` records what was published when on-chain
  money lands (Principle 5). The honest limit is stated in the module docstring
  and pinned by a test: a TRC-20 transfer carries no memo, so per-post
  attribution is unavailable and `confidence` is never better than
  `"correlated"`. It is triggered by the wallet delta, never by a publish, so it
  cannot invent revenue; `count` accompanies every total so an n=1 receipt does
  not read as a trend. Writes nothing until real money arrives - 22 new tests,
  290 pass.

- **1,838 views and $0.00: nothing published gave a reader a way to pay** - fixed
  2026-09-03. The system had two working halves and a gap. `devto.publish` sent
  title, body, description and tags; `status._snapshot_wallet` polled a balance
  nothing was going to change. The code documented its own surrender in a comment
  - "dev.to pays nothing. Publishing is reach, not revenue" - which is half true:
  dev.to pays nothing, but dev.to *readers* can pay and nobody had asked them.
  This was a structural zero, not a conversion-rate problem, so no amount of
  additional reach would have moved it.
  New `bot/earning/payout.py` appends a validated `## Support this work` footer
  inside `devto.publish`, so both products carry it from one call site. No new
  secret (`USDT_WALLET_ADDRESS` is a receive address and already configured), no
  policy change (it is article text, and article publishing is allowed), no LLM
  call (a model can transpose an address character and burned USDT does not come
  back). Address validation is a real checksum, not a shape check - a regex on
  `^T[1-9A-HJ-NP-Za-km-z]{33}$` accepts a two-character transposition, verified
  in the tests. **EIP-55 was implemented on `hashlib.sha3_256` first and it
  rejected all four of the EIP's own test vectors**: NIST changed the padding
  byte, so `payout.keccak256` implements original Keccak-256 rather than adding
  a dependency for one address format. The footer attaches *after* every quality
  gate, because its heading and fence would otherwise pad a too-thin draft past
  `min_words`. Off by default; it publishes under the owner's byline.
  `status["payout"]` records `blocked_reason` so `$0.00` says which kind of zero
  it is. 24 regression tests; 268 pass; principles recorded in
  `docs/passive-income-doctrine.md` and referenced from the top of CLAUDE.md.

- **The bot sourced trending articles from its own dev.to posts** - fixed
  2026-09-03. `trending._FEEDS` reads dev.to's programming tag, which is also
  where the bot publishes, and `_pick_source` only ever filtered against
  *sources it had written from* - never against *articles it had published*. It
  wrote a "trending take" on its own top post (1562 of its 1838 lifetime views)
  and `_ensure_attribution` credited that post in a `## Source` section as
  though it were somebody else's reporting. `fetch_candidates` now takes
  `exclude_authors`; the account's URLs come from `devto_stats.account_urls()`
  (the dev.to API the stats loop already calls), are cached in
  `article_history.own_urls`, and both products read them through
  `devto.own_post_urls()`. No new secret, no hardcoded handle. The newsletter
  had the same hole and features 7 stories an issue, so it was the worse case.

- **Ad copy passed the technical screen on one incidental word** - fixed
  2026-09-03. `is_technical` merged title and summary into one bag of words and
  accepted a single hit anywhere, so a dev.to clothing-store advert - "Family
  Matching Outfits: How to Create Stylish Looks for Every Family Member" - was
  published as a story in a weekly developer digest because its blurb said
  "build" and "data". The title now has to carry a technical term on its own.
  Vocabulary alone cannot catch promotional content ("MATLAB Online Training |
  MATLAB Training Courses Online" is full of technical words), so intent moved
  to `is_spam` (agency/course marketing, roundup padding, non-Latin ad feeds)
  and subject to a new `is_off_topic` (clothing, diet, astrology, visas,
  gambling). Screening on *stricter vocabulary* was tried and **reverted**: it
  dropped "Gemini 3.8 Flash", "Quasar 438B" and "Polars 2.0" off Hacker News.
  16 regression tests added; verified against live feeds, pool still at 40.

- **An empty LLM response was treated as a valid answer** - fixed 2026-09-03.
  All five provider paths in `bot/llm.py` coerced a missing completion to `""`
  and returned it *successfully*, so `complete()` never stepped down its model
  chain and `complete_json*` re-sent the same prompt to the same dead model 3x.
  Cycle #1751 skipped evolution with `First 200 chars: ''` after 3 wasted calls
  to `openrouter/free` while 5 healthy fallbacks went untried; the same hole
  caused both `empty_draft` article rejects. Responses now pass through
  `_require_text`, an empty one steps down the chain like a 404, and the JSON
  wrappers stop reprompting once every provider is exhausted (6 requests where
  the old path spent 18). 4 regression tests added; they fail on the old code.

- **`force articles N` ignored its own count** - fixed 2026-09-02. `commands.py`
  parsed and clamped N to 1-5 and logged it, but `articles.run()` read the
  override only as a truthy cap-bypass and always published exactly one article.
  The publish path is now `_publish_once`, looped N times and stopped at the
  first failure so a dead source pool cannot burn free-tier LLM calls.

- **Dead config files were being fed to the evolution LLM** - fixed 2026-09-02.
  `bot/evolution.py` globs `config/*.json` into the codebase snapshot.
  `config/llm_providers.json` and `config/llm_workflows.json` were not valid JSON
  (Python dict reprs) and named obsolete Gemini/Groq per-role routing;
  `config/error_handling.json` blocked `publishing`, contradicting the live
  `research_and_article_publishing` policy. All three removed, plus the unused
  `bot/utils/` package and three docs describing removed behaviour.

- **Dashboard realtime sync used root-only state** - fixed 2026-05-08. `bot/dashboard.py` now publishes `docs/status.json` and `docs/earnings-log.md` alongside the generated dashboard, and the live UI reloads when a new cycle/version arrives so every panel stays synchronized.

- **Article loop left normal earning throughput below the active cap** - fixed 2026-05-08. Raised `articles.per_cycle` to 3 and increased buyer-intent topic selection to 55% when a CTA is configured.

- **Workflow dependency install listed stdlib modules** - fixed 2026-05-08. Replaced `json`, `pathlib`, and `logging` with the real packages required by the active LLM and earning modules.

- **Article publishes had zero tracked value** - fixed 2026-05-08. Successful dev.to and Medium publishes now use configurable estimated value via `articles.estimated_usd_per_publish`.

- **Groq TPD rate limit blocks evolution** - fixed by adding `ANTHROPIC_API_KEY` secret.

- **Dashboard lacks earnings analysis** - fixed 2026-05-01.

- **Articles topic list dated** - fixed 2026-05-01.

- **Add Gemini + OpenRouter to role-based routing** - fixed 2026-05-02.
  Gemini -> hard thinking (evolution), Groq -> fast replies, OpenRouter -> experiment.
  Dashboard shows per-role provider pills with distinct colors.
  `llm_roles` persisted in status.json.

- **Re-activate `articles_devto`** - active as of v1.3.0 (cycle #440). `DEV_TO_API_KEY` secret present.

- **Earnings breakdown resets on week rollover** - fixed 2026-05-02. Previously accumulated all-time.

- **Evolution dashboard showed `ok` for no-change cycles** - fixed 2026-05-02. Now shows `idle` (blue).

- **Evolution LLM prompt included earnings history + last_earning** - fixed 2026-05-02. Stripped before send.

- **Add `MEDIUM_INTEGRATION_TOKEN`** - fixed in v1.22.0, then reverted in v1.34.0. Medium publishing is outside the dev.to-only policy, so the code path and secret were removed.

- **Dashboard frontend lacked a ranked revenue focus** - fixed in v1.22.1. Added a responsive Research & Revenue Focus section and moved provider/warning colors back through `:root` variables.

- **Article volume strategy was ignored** - fixed 2026-05-08. The orchestrator now reads `articles.per_cycle` from `config/strategy.json` for normal cycles, while owner `force articles N` commands still override it.
