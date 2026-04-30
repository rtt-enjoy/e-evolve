# Evolution TODO

Bot state: v1.1.0 · cycle #418 · $2.77 total · active: `llm_groq`, `articles_devto`

---

## Bugs (break current earning)

### 1. dev.to tag sanitization — FIXED
**Fix applied:** [bot/earning/articles.py:118](bot/earning/articles.py) — tags lowercased and spaces → hyphens before POST.

### 2. Evolution prompt too large for Groq — FIXED
**Fix applied:** [bot/evolution.py](bot/evolution.py) — per-provider `_MAX_READ_BYTES`: Groq=4k, Anthropic=60k. Groq also skips `config/*.json`. Snapshot budget tracked cumulatively; stops adding files once limit reached.

---

## High Priority Improvements

### 3. Tag sanitizer as shared util — FIXED
**Fix applied:** [bot/utils.py](bot/utils.py) — `sanitize_tags()` extracted. [bot/earning/articles.py](bot/earning/articles.py) uses it for both dev.to and Medium.

### 4. Groq model fallback for large prompts — FIXED
**Fix applied:** [bot/llm.py](bot/llm.py) — `_truncate_for_groq()` pre-estimates token budget before send; truncates prompt if over `_GROQ_MAX_PROMPT_TOKENS` (8k).

### 5. Evolution skips on repeated 413 — waste cycles — FIXED
**Fix applied:** [bot/llm.py](bot/llm.py) — retry loop detects `413` in exception string, truncates prompt 40% and retries immediately instead of raising.

---

## Feature Gaps (inactive modules)

| Module | Needs | Est. weekly |
|--------|-------|-------------|
| `llm_anthropic` | `ANTHROPIC_API_KEY` secret in GH repo | Unlocks better evolution |
| `articles_medium` | `MEDIUM_INTEGRATION_TOKEN` | +$0.02/article |
| `twitter` | 4 Twitter secrets | $1–5/week |
| `crypto_binance` | `BINANCE_API_KEY` + `BINANCE_SECRET_KEY` | $0.12 earned already |
| `nft_ethereum` | `ETH_PRIVATE_KEY` + `ETH_WALLET_ADDRESS` | speculative |

**Highest ROI unlock:** Add `ANTHROPIC_API_KEY` → evolution uses Claude → larger context → fixes itself.

---

## Low Priority / Polish

- Dashboard `docs/index.html` shows stale last-cycle earnings ($0.00) — display cumulative trend
- `status.json` suggestions block still shows "Add DEV_TO_API_KEY" even though it's active
- Weekly earnings reset logic in `bot/earnings.py` — verify week boundary math is correct
- Article topics list has 8 entries, cycles every 8 runs — diversify or randomize

---

## Do Not Touch

- `.github/workflows/evolve.yml` — heartbeat, never evolve
- Safety boundaries in `bot/evolution.py` — hardcoded, intentional
