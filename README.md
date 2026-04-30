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
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Paid (higher quality) |

### 3. Trigger the first run

Actions tab → **evolve** workflow → **Run workflow**

### 4. Enable GitHub Pages

Settings → Pages → Source: branch `main`, folder `/docs` → Save

Dashboard live at `https://YOUR_USERNAME.github.io/e-evolve`

---

## Earning Modules

All optional. Add the secret — the next cycle activates that module automatically.

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
