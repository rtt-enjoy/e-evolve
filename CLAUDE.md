# CLAUDE.md — E-Evolve

## Code Change Rules

1. **Don't assume. Don't hide confusion. Surface tradeoffs.**
2. **Minimum code that solves the problem. Nothing speculative.**
3. **Touch only what you must. Clean up only your own mess.**
4. **Define success criteria. Loop until verified.**

---

## Project Overview

E-Evolve is a GitHub Actions bot that runs hourly and refreshes RAG, market research, and earning suggestions. Code evolution and code updates are handled here in Codex. Zero server cost — runs entirely on GitHub Actions free tier.

Current operating policy: API keys are for RAG, research, market analysis, suggestions, and draft-only text. The bot must not use keys to publish articles, post to social media, place trades, mint NFTs, withdraw funds, or comment on external issues.

---

## Architecture

```
bot/main.py          ← 5-phase orchestrator (entry point)
bot/llm.py           ← LLM abstraction (Groq or Anthropic, auto-selected)
bot/status.py        ← Phase 1: load/save status.json
bot/commands.py      ← Phase 2: owner commands (command.txt or GitHub Issues)
bot/evolution.py     ← legacy evolution engine; not called by default
bot/earnings.py      ← cumulative earnings tracker + weekly reset
bot/dashboard.py     ← writes docs/index.html + earnings-log.md
bot/git_utils.py     ← git commit helpers
bot/earning/
  articles.py        ← legacy publishing module; not called by default
  twitter.py         ← legacy social module; not called by default
  crypto.py          ← legacy trading module; not called by default
  nft.py             ← legacy minting module; not called by default
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
Phase 3: Evolution — skipped; Codex owns code changes, API keys stay research-only
Phase 4: Research — refresh suggestion-only research queues
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

Publishing, posting, trading, minting, and payout secrets do not activate runtime actions. If such keys exist, they are treated as research context only.

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
force articles N         # ignored: publishing is disabled
force trade aggressive   # ignored: trading is disabled
force mint N             # ignored: minting is disabled
skip evolution           # skip Phase 3 this cycle
reset earnings           # zero this_week_usd
post thread              # ignored: posting is disabled
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

Tunable by owner or changed here in Codex:

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
