# 🤖 E-Evolve

An autonomous, self-improving bot that earns money and evolves its own codebase —
powered entirely by **GitHub Actions** at zero server cost.

[![evolve](https://github.com/YOUR_USERNAME/e-evolve/actions/workflows/evolve.yml/badge.svg)](https://github.com/YOUR_USERNAME/e-evolve/actions/workflows/evolve.yml)

---

## How it works

Every hour at `:17`, one complete cycle runs:

```
Status Check → Evolution (LLM improves code) → Earning Actions → State Update
```

| Phase | What happens |
|-------|-------------|
| **Status** | Reads `status.json`, detects which secrets are present, builds cycle snapshot |
| **Commands** | Reads `command.txt` or GitHub Issues labelled `bot-command` for owner instructions |
| **Evolution** | Sends codebase + status to Groq/Claude; receives and commits code improvements |
| **Earning** | Runs all active modules: articles, Twitter threads, crypto trading, NFT minting |
| **Update** | Saves `status.json`, regenerates `docs/index.html` dashboard, commits everything |

---

## 🚀 Setup (5 minutes)

### 1. Fork this repo (keep it public for free GitHub Pages)

### 2. Add the minimum required secret

**Repo → Settings → Secrets and variables → Actions → New repository secret**

| Secret | Where to get it | Cost |
|--------|----------------|------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | **Free** |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Paid (higher quality) |

You only need **one** of the above.

### 3. Trigger the first run manually

Actions tab → **evolve** workflow → **Run workflow** button

### 4. Enable GitHub Pages

Settings → **Pages** → Source: branch `main` → folder `/docs` → **Save**

Your dashboard will be live at `https://YOUR_USERNAME.github.io/e-evolve`

---

## 💰 Earning Modules

All optional. Add the secret → the very next cycle activates that module automatically.

### Articles (dev.to + Medium)
| Secret | How to get |
|--------|-----------|
| `DEV_TO_API_KEY` | [dev.to → Settings → Extensions](https://dev.to/settings/extensions) |
| `MEDIUM_INTEGRATION_TOKEN` | [medium.com/me/settings](https://medium.com/me/settings) → Integration tokens |

### Twitter / X Threads
| Secret | Notes |
|--------|-------|
| `TWITTER_API_KEY` | Twitter Developer Portal — needs "Read and Write" permission |
| `TWITTER_API_SECRET` | " |
| `TWITTER_ACCESS_TOKEN` | " |
| `TWITTER_ACCESS_SECRET` | " |

### Crypto Trading (Binance)
| Secret | Notes |
|--------|-------|
| `BINANCE_API_KEY` | Enable **Spot trading** only — disable withdrawals |
| `BINANCE_SECRET_KEY` | " |

> ⚠️ Automated trading involves financial risk. Start with a small balance.

### NFT Minting (Ethereum)
| Secret | Notes |
|--------|-------|
| `ETH_PRIVATE_KEY` | Use a dedicated wallet with minimal funds |
| `ETH_WALLET_ADDRESS` | Corresponding public address |
| `NFT_CONTRACT_ADDRESS` | Address of a pre-deployed ERC-721 contract |
| `NFT_STORAGE_TOKEN` | [nft.storage](https://nft.storage) — free IPFS pinning |

---

## 🧬 Self-Evolution

Each cycle the bot reads its own code and asks the LLM to improve it.
Changes are committed automatically. The dashboard shows exactly what changed.

**Safety boundaries (hardcoded — cannot be evolved away):**
- Writes only to: `bot/`, `docs/`, `config/`, `requirements.txt`, `version.txt`
- Never touches: `.github/` (your workflow is safe)
- Python files syntax-checked before writing
- Original files backed up in `.evolution_backups/` (not committed)

---

## 🎮 Owner Commands

Write commands in `command.txt` and commit. The next cycle executes them and clears the file.

```
force articles 3         # post 3 articles this cycle
force trade aggressive   # raise trade risk to 5 %
force mint 2             # mint 2 NFTs
skip evolution           # skip evolution this cycle
reset earnings           # zero the weekly counter
post thread              # force a Twitter thread
status report            # dump full status to workflow log
```

Or create a GitHub Issue with the command as the title and add the label `bot-command`.

---

## 📁 Project Structure

```
.github/workflows/evolve.yml  ← the hourly workflow (never evolved)
bot/
  main.py                     ← orchestrator
  llm.py                      ← LLM abstraction (Groq / Anthropic)
  status.py                   ← Phase 1: load/save state
  evolution.py                ← Phase 3: self-improvement
  commands.py                 ← owner command system
  earnings.py                 ← cumulative earnings + weekly reset
  dashboard.py                ← HTML dashboard + earnings log
  git_utils.py                ← git commit helpers
  earning/
    articles.py               ← dev.to + Medium publishing
    twitter.py                ← Twitter/X threads
    crypto.py                 ← Binance spot trading
    nft.py                    ← Ethereum NFT minting
docs/
  index.html                  ← GitHub Pages dashboard (auto-updated)
  .nojekyll                   ← disables Jekyll processing
status.json                   ← shared state (auto-updated each cycle)
earnings-log.md               ← human-readable earnings history
version.txt                   ← current bot version
command.txt                   ← owner command input
config/strategy.json          ← tunable strategy parameters
```

---

## License

MIT — fork, evolve, earn.
