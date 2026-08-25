# Research Modules

Each module lives in `bot/earning/`. All follow the same contract:

```python
def run(llm: LLMClient, status: dict) -> list[dict]:
    # Returns list of action dicts, one per attempt
    # Each dict: { platform, success, error?, amount_usd?, ... }
```

Exceptions are caught by `main.py._module()` — a crashed module does not stop the cycle.

---

Only two modules run: `code_techs` (research/suggestions only) and `articles`
(publishes to dev.to when `DEV_TO_API_KEY` is set). Social posting, crypto
trading, NFT minting, payouts, and external comments are blocked by policy —
the modules that once implemented them have been removed from the tree.

## Code Techs (`bot/earning/code_techs.py`)

**Activates when:** enabled in `config/strategy.json` or `CODE_TECH_EARN_ENABLED=1`

**What it does:**
1. Searches for overlooked code-maintenance opportunities, then falls back to a local playbook if search is unavailable.
2. Ranks leads by payout signal, proof quality, and neglected maintenance pain.
3. Writes `docs/code-tech-opportunities.md` with requirements, focus areas, strategy, avoid patterns, and ranked next steps.
4. Returns an action dict with `platform`, `success`, `opportunity_count`, and `target_usd_per_day`.
5. Never posts comments or pursues leads automatically.

**Strategy:** favor boring work that most people skip but owners actually need:
failing CI, stale dependencies, broken quickstarts, packaging drift, runtime
compatibility, release-note gaps, and small integration bugs. Start with public
proof, keep the first patch easy to review, then turn repeated pain into a
fixed-scope maintenance offer.

**Config** (`config/strategy.json`):
```json
{
  "code_techs": {
    "enabled": true,
    "refresh_hours": 24,
    "daily_target_usd": 10.0,
    "max_items": 8,
    "min_score": 55,
    "requirements": [],
    "underserved_focus": [],
    "strategy_playbook": [],
    "avoid_patterns": [],
    "github_searches": []
  }
}
```

**Disable:** set `CODE_TECH_EARN_ENABLED=0`.

---

## Articles (`bot/earning/articles.py`)

**Activates when:** `DEV_TO_API_KEY` is present. Without it the module skips
silently.

**What it does:**
1. `trending.fetch_candidates()` finds a real tech article from the last 24h via
   free keyless feeds; `_pick_source()` takes the top-ranked one not already in
   `status["article_history"]`, so a source is used at most once ever.
2. Asks the LLM for an *improved, original* piece on that subject -- added value
   (working code, tradeoffs, failure modes), never a reword.
3. Runs the publish gates in order: `_strip_fabricated_tables()`,
   `_fabrication_problems()` (hard reject), `_format_problems()` +
   `_tone_problems()` (one revision call), `_too_similar_to_source()`,
   `_duplicate_reason()`, `_ensure_attribution()`.
4. Posts to dev.to via REST API and returns an action dict with `platform`,
   `success`, `title`, `url`, and `estimated_usd`.

If no fresh source is found or the LLM fails, it publishes nothing. There is
deliberately no fallback article -- a static fallback is what produced the
duplicate flood on dev.to.

**Config** (`config/strategy.json`):
```json
{
  "articles": {
    "max_articles_per_cycle": 1,
    "min_interval_hours": 6,
    "source_max_age_hours": 24,
    "history_limit": 200,
    "min_words": 700
  }
}
```

**Override:** `force articles N` command posts N articles in one cycle.

---

## Adding a New Module

1. Create `bot/earning/yourmodule.py` with `def run(llm, status) -> list[dict]:`
2. Add feature key + required secrets to `FEATURE_MAP` in `bot/status.py`
3. Add activation check in `bot/main.py` Phase 4
4. No other changes needed — the module will auto-activate when secrets are present
