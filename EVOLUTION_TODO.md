# Evolution TODO

Bot state: v1.37.3 - cycle #1755 - active: `llm_anthropic`, `llm_gemini`, `llm_openrouter`, `llm_groq`, `articles_devto`, `usdt_wallet`

**Read [`docs/passive-income-doctrine.md`](docs/passive-income-doctrine.md) before
working this list.** It ranks channels by what runs unattended and carries the
scored candidate table, so a cycle does not re-derive the same refused ideas.

---

## Bugs (break current earning)

_(none open)_

---

## High Priority - Earning

- **Put the validated wallet address on the public dashboard.** The doctrine's
  channel table scores this as the lowest-effort remaining win: `docs/` is
  already served publicly by GitHub Pages, the address is already
  checksum-validated in `bot/earning/payout.py`, and `status["payout"]` already
  carries the masked form and the live/blocked state. It needs no new secret, no
  owner action, and no policy change - the same five rows that justified the
  article footer. `bot/dashboard.py` regenerates `docs/index.html` each cycle, so
  the change goes there, not in the HTML. Use `payout.resolve_address()` for the
  full address rather than the masked one from status, and use the existing CSS
  variables - never a hardcoded hex.

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
