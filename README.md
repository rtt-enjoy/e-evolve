# E-Evolve

Autonomous bot that researches earning opportunities while code evolution happens here in Codex — powered entirely by **GitHub Actions** at zero server cost.

Current mode: API keys are used for RAG, online research, market analysis, suggestions, and draft-only text. The bot does not publish articles, post social threads, trade crypto, mint NFTs, withdraw funds, or comment on external issues.

[![evolve](https://github.com/YOUR_USERNAME/e-evolve/actions/workflows/evolve.yml/badge.svg)](https://github.com/YOUR_USERNAME/e-evolve/actions/workflows/evolve.yml)

---

## How It Works

Every hour at `:17`, one complete cycle runs:

```
Init LLM → Status Check → Owner Commands → Codex-Owned Evolution Skip → Research Suggestions → State Update
```

| Phase | What happens |
|-------|-------------|
| **Status** | Load `status.json`, detect active features from present secrets |
| **Commands** | Read `command.txt` or GitHub Issues labelled `bot-command` |
| **Evolution** | Skip automatic code changes; Codex owns implementation |
| **Research** | Refresh RAG/research queues and ranked earning suggestions only |
| **Update** | Save `status.json`, publish dashboard data files, commit all |

---

## Quick Start (5 minutes)

### 1. Fork this repo

Keep it public for free GitHub Pages.

### 2. Add one LLM secret

**Repo → Settings → Secrets and variables → Actions → New repository secret**

| Secret | Source | Cost |
|--------|--------|------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | Free |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Free tier |
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai/keys) | Free models available |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Paid (higher quality) |

For local runs, copy `.env.example` to `.env` and fill the same variable names.
`.env` stays ignored by git; GitHub Actions uses repository secrets online.
See [`docs/environment.md`](docs/environment.md) for the complete environment
key reference.

### 3. Trigger the first run

Actions tab → **evolve** workflow → **Run workflow**

### 4. Enable GitHub Pages

Settings → Pages → Source: branch `main`, folder `/docs` → Save

Dashboard live at `https://YOUR_USERNAME.github.io/e-evolve`

The dashboard contract is documented in
[`docs/frontend-dashboard.md`](docs/frontend-dashboard.md). It defines the
required workflow, evolution, error, suggestion, module, and secret-readiness
signals that the frontend must keep visible.

The dashboard UI is a static React/Vite/Tailwind app in `frontend/`. Python
stays the backend data publisher and writes `docs/status.json` plus
`docs/earnings-log.md` during each cycle.

### No-ID Free Self-Earn Setup

Start here when you cannot use Binance identity verification, Claude premium
features, phone-gated social APIs, paid services, or funded wallets:

1. Use the default code-tech opportunity flow. It needs no external secret.
2. Add `GROQ_API_KEY` or `GEMINI_API_KEY` for RAG/research/suggestions.
3. Optional: add `OPENROUTER_API_KEY` for free-model research fallback.
4. Keep publishing, posting, trading, payout, and minting keys out of the runtime path. If those keys exist in the environment, the bot treats them as setup/suggestion context only and does not call external write APIs.

### Code-Tech Opportunity Flow

The bot also runs an independent code-tech research flow by default. It does not
depend on articles, social posting, crypto, or NFTs. Once per configured cadence,
it searches for overlooked developer work an AI agent can handle automatically:
CI failures, dependency migrations, broken examples, flaky tests, starter
template repairs, deprecation cleanup, and niche package maintenance. Results
are written to `docs/code-tech-opportunities.md`.

The target is practical pipeline creation, for example finding enough small
code-maintenance work to pursue `$10/day`. Discovery is not counted as earned
money; confirmed earnings should still come from owner-confirmed payouts or
reconciliation. Disable it with `CODE_TECH_EARN_ENABLED=0` or tune it in
`config/strategy.json` under `code_techs`.

The strategy deliberately looks where AI can do the boring part without private
context: broken quickstarts in small SDKs, runtime drift after Python or Node
releases, stale packaging metadata, ignored CI warnings, release-note gaps, and
data import/export bugs in unflashy integrations. Each lead should have public
proof and a bounded first fix before it deserves deep work.

---

## Research Modules

Only research/read-only modules run automatically. Legacy action modules remain in the tree for reference, but the orchestrator no longer activates publishing, posting, trading, payout, or minting from secrets.

### Code Techs (independent)

No secret required. Uses public GitHub issue search when available and falls
back to a local playbook when the network is unavailable. It writes ranked
suggestions only and does not comment on external issues.

---

## Code Evolution

Code evolution is handled here in Codex. The hourly bot records the skipped evolution phase and keeps API keys limited to RAG, research, market analysis, suggestions, and drafts.

**Safety boundaries (hardcoded — cannot be evolved away):**
- Writes only to: `bot/`, `docs/`, `config/`, `requirements.txt`, `version.txt`
- Never touches: `.github/` — your workflow is always safe
- Python files AST-checked before writing
- Originals backed up to `.evolution_backups/` (not committed)
- Max 3 file changes per cycle

---

## Owner Commands

Write commands in `command.txt` and commit. The next cycle executes and clears them.
Also works via GitHub Issues with label `bot-command`.

```
force articles 3         # ignored: publishing is disabled
force trade aggressive   # ignored: trading is disabled
force mint 2             # ignored: minting is disabled
skip evolution           # skip LLM evolution this cycle
reset earnings           # zero the weekly counter
post thread              # ignored: posting is disabled
status report            # dump full status to workflow log
```

---

## Project Structure

```
.github/workflows/evolve.yml  ← hourly workflow (never evolved)
bot/
  main.py                     ← 5-phase orchestrator
  llm.py                      ← LLM client (Groq / Anthropic, auto-selected)
  status.py                   ← Phase 1: load/save state
  commands.py                 ← Phase 2: owner command system
  evolution.py                ← Phase 3: self-improvement engine
  earnings.py                 ← cumulative earnings + weekly reset
  dashboard.py                ← dashboard data publisher + earnings log
  git_utils.py                ← git commit helpers
  earning/
    articles.py               ← legacy publishing module; not called by default
    twitter.py                ← legacy social module; not called by default
    crypto.py                 ← legacy trading module; not called by default
    nft.py                    ← legacy minting module; not called by default
config/
  strategy.json               ← tunable strategy parameters
frontend/
  src/                        ← React/Vite/Tailwind dashboard source
  package.json                ← frontend build scripts
docs/
  index.html                  ← built GitHub Pages dashboard
  assets/                     ← built frontend assets
  .nojekyll                   ← disables Jekyll processing
status.json                   ← persisted state (auto-updated each cycle)
earnings-log.md               ← human-readable earnings history
version.txt                   ← current bot version (X.Y.Z)
command.txt                   ← owner command input
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
npm run build
```

`npm run build` writes the static app to `docs/` without deleting the existing
documentation files. The app reads `docs/status.json` in production.

---

## License

MIT — fork, evolve, earn.
