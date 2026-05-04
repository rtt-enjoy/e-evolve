# CLAUDE.md — E-Evolve

## Code Change Rules

1. **Don't assume. Don't hide confusion. Surface tradeoffs.**
2. **Minimum code that solves the problem. Nothing speculative.**
3. **Touch only what you must. Clean up only your own mess.**
4. **Define success criteria. Loop until verified.**

---

## Project Overview

E-Evolve is a self-improving GitHub Actions bot that runs hourly, evolves its own codebase via LLM, and executes earning modules (articles, Twitter, crypto, NFT). Zero server cost — runs entirely on GitHub Actions free tier.

---

## Architecture

```
bot/main.py          ← 5-phase orchestrator (entry point)
bot/llm.py           ← LLM abstraction (Groq or Anthropic, auto-selected)
bot/status.py        ← Phase 1: load/save status.json
bot/commands.py      ← Phase 2: owner commands (command.txt or GitHub Issues)
bot/evolution.py     ← Phase 3: LLM reads codebase, proposes changes, applies them
bot/earnings.py      ← cumulative earnings tracker + weekly reset
bot/dashboard.py     ← writes docs/index.html + earnings-log.md
bot/git_utils.py     ← git commit helpers
bot/earning/
  articles.py        ← dev.to + Medium publishing
  twitter.py         ← Twitter/X threads
  crypto.py          ← Binance spot trading
  nft.py             ← Ethereum NFT minting
.github/workflows/evolve.yml  ← hourly scheduler (never evolved)
config/strategy.json ← tunable strategy parameters
status.json          ← persisted bot state (auto-updated each cycle)
version.txt          ← current bot version (X.Y.Z)
command.txt          ← owner command input
```

---

## Cycle Flow (5 Phases)

```
Phase 0: Init LLM (Anthropic > Groq, priority order)
Phase 1: Status   — load status.json, detect active features from env secrets
Phase 2: Commands — read command.txt + GitHub Issues labelled "bot-command"
Phase 3: Evolution — send codebase to LLM, apply safe code changes, commit
Phase 4: Earning  — run active modules: articles, twitter, crypto, nft
Phase 5: Update   — save status.json, write dashboard, commit
```

---

## Safety Boundaries (evolution.py — hardcoded, cannot be LLM-overridden)

- Writes only to: `bot/`, `docs/`, `config/`, `requirements.txt`, `version.txt`
- Never touches: `.github/`, `.git/`
- No path traversal (`..` rejected)
- Python files AST-parsed before writing
- Max 3 file changes per cycle
- Originals backed up to `.evolution_backups/` before overwrite

---

## Feature Activation

Features activate automatically when their secrets are present in env.

| Feature | Required Secrets |
|---------|-----------------|
| `llm_anthropic` | `ANTHROPIC_API_KEY` |
| `llm_gemini` | `GEMINI_API_KEY` |
| `llm_openrouter` | `OPENROUTER_API_KEY` |
| `llm_groq` | `GROQ_API_KEY` |
| `articles_devto` | `DEV_TO_API_KEY` |
| `articles_medium` | `MEDIUM_INTEGRATION_TOKEN` |
| `twitter` | `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET` |
| `crypto_binance` | `BINANCE_API_KEY`, `BINANCE_SECRET_KEY` |
| `nft_ethereum` | `ETH_PRIVATE_KEY`, `ETH_WALLET_ADDRESS` |

---

## LLM Client (bot/llm.py)

- Priority: `ANTHROPIC_API_KEY` → `GROQ_API_KEY`
- Groq default model: `llama-3.3-70b-versatile` (fallback chain to smaller)
- Anthropic default model: `claude-sonnet-4-6` (fallback chain)
- All calls retry 3× with exponential backoff
- `complete_json()` appends JSON-only instruction and strips markdown fences

---

## Owner Commands

Write to `command.txt`, commit. Next cycle executes and clears them.
Also works via GitHub Issues with label `bot-command`.

```
force articles N         # post N articles this cycle
force trade aggressive   # raise trade risk to 5%
force mint N             # mint N NFTs
skip evolution           # skip Phase 3 this cycle
reset earnings           # zero this_week_usd
post thread              # force Twitter thread
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

---

## Strategy Config (config/strategy.json)

Tunable by owner or evolved by LLM:

```json
{
  "articles":  { "per_cycle": 1, "min_words": 600 },
  "crypto":    { "risk_per_trade_pct": 0.02, "min_usdt_balance": 10.0, "symbols": ["BTCUSDT", "ETHUSDT"] },
  "nft":       { "per_cycle": 1, "chain": "ethereum" },
  "twitter":   { "min_tweets": 5, "max_tweets": 7 }
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
