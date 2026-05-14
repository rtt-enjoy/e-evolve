# Architecture

## Cycle Execution

```
bot/main.py (entry: python -m bot.main)
│
├─ Phase 0: LLMClient()          bot/llm.py
│    └─ picks provider: ANTHROPIC_API_KEY → anthropic, else GROQ_API_KEY → groq
│
├─ Phase 1: status.load()        bot/status.py
│    ├─ reads status.json (defaults if missing)
│    └─ snapshot(): increments total_runs, detects active features from env
│
├─ Phase 2: commands.read()      bot/commands.py
│    ├─ reads command.txt (clears executed lines)
│    └─ reads GitHub Issues labelled "bot-command" (closes each after reading)
│
├─ Phase 3: evolution.run()      bot/evolution.py
│    ├─ reads codebase (bot/**/*.py, config/*.json, requirements.txt)
│    ├─ sends to LLM with _SYSTEM prompt → expects JSON {version, summary, changes, suggestions}
│    ├─ validates each change: path safety, AST check for .py
│    ├─ backs up originals → writes new files
│    └─ commits changed files + version.txt
│
├─ Phase 4: earning modules      bot/earning/*.py
│    ├─ articles.py  (active if DEV_TO_API_KEY or MEDIUM_INTEGRATION_TOKEN)
│    ├─ twitter.py   (active if all 4 TWITTER_* keys)
│    ├─ crypto.py    (active if BINANCE_API_KEY + BINANCE_SECRET_KEY)
│    └─ nft.py       (active if ETH_PRIVATE_KEY + ETH_WALLET_ADDRESS)
│
└─ Phase 5: state update
     ├─ earnings.update()        bot/earnings.py   — accumulate USD, weekly reset
     ├─ dashboard.write_log()    bot/dashboard.py  — append earnings-log.md
     ├─ dashboard.write_html()   bot/dashboard.py  — regenerate docs/index.html
     └─ git commit status.json, earnings-log.md, docs/index.html, command.txt, version.txt
```

## LLM Client

```
LLMClient
├─ complete(prompt, system, max_tokens, temperature) → LLMResponse
│    └─ retries 3× with exponential backoff (2s, 4s)
└─ complete_json(prompt, system, max_tokens) → dict
     └─ appends JSON-only instruction → calls complete() → parse_json()
          └─ strips markdown fences → json.loads → fallback regex extraction
```

## Data Flow

```
GitHub Secrets (env vars)
    ↓ detected by status.py → active_features[]
    ↓ consumed by earning/*.py at runtime

status.json  (persisted state)
    ↓ loaded each cycle
    ↓ enriched with cycle snapshot
    ↓ passed through all phases
    ↓ saved at end

command.txt  (owner input)
    ↓ read by commands.py
    ↓ parsed into _overrides dict (runtime-only, not persisted)
    ↓ affects phase 3 (skip_evolution) and phase 4 (force_articles, etc.)
```

## Evolution Safety Stack

```
LLM proposes changes[]
    ↓ _is_safe(path): rejects "..", ".github/", ".git/"; allows only ALLOWED_PREFIXES
    ↓ _is_valid_python(content): ast.parse() — rejects on SyntaxError
    ↓ MAX_CHANGES = 3: only first 3 changes applied
    ↓ _backup(filepath): copies original to .evolution_backups/ before overwrite
    ↓ dest.write_text(): writes new content
```

## Dashboard Live Updates

`docs/index.html` (GitHub Pages) polls `status.json` every 60 seconds via `fetch()`.
No server required — the browser fetches the JSON directly from the same Pages origin.

Dynamic elements updated without page reload:
- Workflow Status: phase health for status, commands, evolution, earning, update
- Live Change Pulse: new cycles, evolution updates, error changes, and newly
  detected secret names compared with the previous poll
- Problems And Corrections: stale workflow state, errors, failed actions,
  evolution failures, and missing high-impact setup secrets
- Secret Readiness: configured secret names plus per-feature readiness counts
- Header: version pill, provider pills, feature badges, last-cycle time, age pill
- KPI cards: total earned, this-week earnings, cycle count, active module count
- Footer: live indicator dot flashes green on each successful fetch

The page has no `meta http-equiv="refresh"` — the JS polling replaces it.
Fields that require a full re-render (suggestions, evolution log, action table) are still
regenerated server-side each cycle when `dashboard.write_html()` runs in Phase 5.

The frontend implementation contract lives in `docs/frontend-dashboard.md`.

## Commit Strategy

Two commits per cycle (when applicable):

1. Evolution commit: `🧬 evolve vX.Y.Z: <summary>` — changed source files + version.txt
2. State commit: `📊 cycle #N +$X.XXXX Xs` — status.json, earnings-log.md, docs/index.html, command.txt, version.txt

GitHub Actions workflow handles push conflicts via `git pull --rebase` retry.
