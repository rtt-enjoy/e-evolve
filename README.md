# E-Evolve

Autonomous, self-improving bot that earns money and evolves its own codebase — powered entirely by **GitHub Actions** at zero server cost.

[![evolve](https://github.com/YOUR_USERNAME/e-evolve/actions/workflows/evolve.yml/badge.svg)](https://github.com/YOUR_USERNAME/e-evolve/actions/workflows/evolve.yml)

---

## How It Works

Every hour at `:17`, one complete cycle runs:

```
Init LLM → Status Check → Owner Commands → LLM Evolution → Earning Actions → State Update
```

| Phase | What happens |
|-------|-------------|
| **Status** | Load `status.json`, detect active features from present secrets |
| **Commands** | Read `command.txt` or GitHub Issues labelled `bot-command` |
| **Evolution** | Send codebase + status to LLM; receive and apply code improvements |
| **Earning** | Run active modules: articles, Twitter threads, crypto trading, NFT minting |
| **Update** | Save `status.json`, regenerate `docs/index.html` dashboard, commit all |

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

### 3. Trigger the first run

Actions tab → **evolve** workflow → **Run workflow**

### 4. Enable GitHub Pages

Settings → Pages → Source: branch `main`, folder `/docs` → Save

Dashboard live at `https://YOUR_USERNAME.github.io/e-evolve`

The dashboard contract is documented in
[`docs/frontend-dashboard.md`](docs/frontend-dashboard.md). It defines the
required workflow, evolution, error, suggestion, module, and secret-readiness
signals that the frontend must keep visible.

### No-Money Self-Earn Setup

Start with the free content loop:

1. Add `GROQ_API_KEY`.
2. Add `DEV_TO_API_KEY`.
3. Add optional GitHub Actions variables, not secrets:
   - `EARN_CTA_URL`: sponsor, tip, newsletter, affiliate, portfolio, or product link.
   - `EARN_CTA_LABEL`: link text shown at the end of each article.

When `EARN_CTA_URL` is set, the article loop periodically switches to buyer-intent topics from
`config/strategy.json` so the content is still useful, but closer to people who might click,
subscribe, sponsor, or buy.

CTA links are tagged with `utm_source`, `utm_medium`, and the configured
`articles.cta_utm_campaign` value so dev.to, Medium, and Twitter/X traffic can be compared later.

Keep crypto and NFT modules disabled until you have funds you can afford to risk.

### Code-Tech Opportunity Flow

The bot also runs an independent code-only earning flow by default. It does not
depend on articles, social posting, crypto, or NFTs. Once per configured cadence,
it searches for overlooked developer work such as small paid OSS issues, CI
failures, dependency migrations, broken examples, flaky tests, and niche package
maintenance. Results are written to `docs/code-tech-opportunities.md`.

The target is practical pipeline creation, for example finding enough small
code-maintenance work to pursue `$10/day`. Discovery is not counted as earned
money; confirmed earnings should still come from actual payouts or owner
reconciliation. Disable it with `CODE_TECH_EARN_ENABLED=0` or tune it in
`config/strategy.json` under `code_techs`.

The strategy deliberately looks where most people do not: broken quickstarts in
small SDKs, runtime drift after Python or Node releases, stale packaging
metadata, ignored CI warnings, release-note gaps, and data import/export bugs in
unflashy integrations. Each lead should have public proof, a bounded first fix,
and some visible owner or payer signal before it deserves deep work.

---

## Earning Modules

All optional. Add the secret — the next cycle activates that module automatically.

### Code Techs (independent)

No secret required. Uses public GitHub issue search when available and falls
back to a local playbook when the network is unavailable.

### Articles (dev.to + Medium)

| Secret | Source |
|--------|--------|
| `DEV_TO_API_KEY` | dev.to → Settings → Extensions |
| `MEDIUM_INTEGRATION_TOKEN` | medium.com/me/settings → Integration tokens |

### Twitter / X Threads

| Secret | Notes |
|--------|-------|
| `TWITTER_API_KEY` | Twitter Developer Portal — needs Read+Write permission |
| `TWITTER_API_SECRET` | " |
| `TWITTER_ACCESS_TOKEN` | " |
| `TWITTER_ACCESS_SECRET` | " |

### Crypto Trading (Binance)

| Secret | Notes |
|--------|-------|
| `BINANCE_API_KEY` | Enable Spot trading only — disable withdrawals |
| `BINANCE_SECRET_KEY` | " |

> **Warning:** Automated trading involves financial risk. Start with a small balance.

### NFT Minting (Ethereum)

| Secret | Notes |
|--------|-------|
| `ETH_PRIVATE_KEY` | Use a dedicated wallet with minimal funds |
| `ETH_WALLET_ADDRESS` | Corresponding public address |
| `NFT_CONTRACT_ADDRESS` | Pre-deployed ERC-721 contract address |
| `NFT_STORAGE_TOKEN` | [nft.storage](https://nft.storage) — free IPFS pinning |

---

## Self-Evolution

Each cycle the bot reads its own source and asks the LLM to improve it. Changes are committed automatically. The dashboard shows exactly what changed.

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
force articles 3         # post 3 articles this cycle
force trade aggressive   # raise trade risk to 5%
force mint 2             # mint 2 NFTs
skip evolution           # skip LLM evolution this cycle
reset earnings           # zero the weekly counter
post thread              # force a Twitter thread
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
  dashboard.py                ← HTML dashboard + earnings log
  git_utils.py                ← git commit helpers
  earning/
    articles.py               ← dev.to + Medium publishing
    twitter.py                ← Twitter/X threads
    crypto.py                 ← Binance spot trading
    nft.py                    ← Ethereum NFT minting
config/
  strategy.json               ← tunable strategy parameters
docs/
  index.html                  ← GitHub Pages dashboard (auto-updated)
  .nojekyll                   ← disables Jekyll processing
status.json                   ← persisted state (auto-updated each cycle)
earnings-log.md               ← human-readable earnings history
version.txt                   ← current bot version (X.Y.Z)
command.txt                   ← owner command input
```

---

## License

MIT — fork, evolve, earn.
