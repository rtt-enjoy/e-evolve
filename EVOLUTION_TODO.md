# Evolution TODO

Bot state: v1.1.0 · cycle #418 · $2.77 total · active: `llm_groq`, `articles_devto`

---

## Bugs (break current earning)

### 1. dev.to tag sanitization — BREAKING
**Error:** `HTTP 422: Tag "python automation" contains non-alphanumeric or prohibited unicode characters`  
**Cause:** LLM returns tags with spaces (e.g. `"python automation"`). dev.to requires slug-style tags.  
**Fix:** Strip/replace spaces with hyphens in `_post_devto()` before POST, and lowercase all tags.  
**File:** [bot/earning/articles.py](bot/earning/articles.py) — `_post_devto()` around line 113  
**Impact:** Every article cycle fails silently. Zero earnings until fixed.

### 2. Evolution prompt too large for Groq — BREAKING
**Error:** `413 Request too large — Requested 24376 tokens, Limit 12000 TPM`  
**Cause:** `_read_codebase()` sends full source (~1900 lines) + status JSON to Groq. Exceeds free-tier TPM.  
**Fix options (pick one):**
- A. Reduce `MAX_READ_BYTES` from 20k → 8k and skip `config/*.json` from snapshot
- B. Send only changed/relevant files (diff-based selection)
- C. Summarize codebase structure instead of full source  
**File:** [bot/evolution.py](bot/evolution.py) — `_read_codebase()` line 109, `MAX_READ_BYTES` line 30  
**Impact:** Evolution has never succeeded in recent cycles. Bot cannot self-improve.

---

## High Priority Improvements

### 3. Tag sanitizer as shared util
Once bug #1 fixed, extract tag cleaning to `bot/utils.py` so Medium module reuses it.

### 4. Groq model fallback for large prompts
`bot/llm.py` has fallback chain but all Groq models share same org TPM limit.  
Add token pre-estimate before sending — if > 8k tokens, truncate prompt not fail.

### 5. Evolution skips on repeated 413 — waste cycles
Currently retries 3× then records error. Should detect 413 and reduce payload before retry.  
**File:** [bot/llm.py](bot/llm.py) — retry loop

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
