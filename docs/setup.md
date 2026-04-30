# Setup Guide

## Minimum Setup (5 minutes)

### 1. Fork the repo

Keep it public — required for free GitHub Pages and free Actions minutes.

### 2. Add one LLM secret

Repo → Settings → Secrets and variables → Actions → **New repository secret**

| Secret | Source | Cost |
|--------|--------|------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | Free |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Paid (higher quality) |

Only one is required. If both are present, Anthropic takes priority.

### 3. Trigger first run

Actions tab → **evolve** → **Run workflow**

Watch the logs. A successful first run commits `status.json` and `docs/index.html`.

### 4. Enable GitHub Pages

Settings → Pages → Source: branch `main`, folder `/docs` → **Save**

Dashboard: `https://YOUR_USERNAME.github.io/e-evolve`

---

## Earning Module Setup

### Articles

| Secret | Source |
|--------|--------|
| `DEV_TO_API_KEY` | dev.to → Settings → Extensions |
| `MEDIUM_INTEGRATION_TOKEN` | medium.com/me/settings → Integration tokens |

Either or both. Each present secret activates the corresponding platform.

### Twitter / X

All four required:

| Secret | Notes |
|--------|-------|
| `TWITTER_API_KEY` | Developer Portal — needs Read+Write permission |
| `TWITTER_API_SECRET` | " |
| `TWITTER_ACCESS_TOKEN` | " |
| `TWITTER_ACCESS_SECRET` | " |

### Crypto (Binance)

| Secret | Notes |
|--------|-------|
| `BINANCE_API_KEY` | Enable Spot trading only — **disable withdrawals** |
| `BINANCE_SECRET_KEY` | " |

> **Warning:** Start with a small balance. LLM-driven trading is not guaranteed to be profitable.

### NFT (Ethereum)

| Secret | Notes |
|--------|-------|
| `ETH_PRIVATE_KEY` | Use a dedicated wallet with minimal funds |
| `ETH_WALLET_ADDRESS` | Corresponding public address |
| `NFT_CONTRACT_ADDRESS` | Pre-deployed ERC-721 contract |
| `NFT_STORAGE_TOKEN` | [nft.storage](https://nft.storage) — free IPFS pinning |

---

## Local Development

```bash
# 1. Clone your fork
git clone https://github.com/YOUR_USERNAME/e-evolve
cd e-evolve

# 2. Install deps
pip install -r requirements.txt

# 3. Create .env with your keys
cat > .env << 'EOF'
GROQ_API_KEY=your_key_here
# ANTHROPIC_API_KEY=optional
# DEV_TO_API_KEY=optional
EOF

# 4. Run one cycle
python -m bot.main
```

`python-dotenv` loads `.env` automatically when running locally. CI ignores it (uses GitHub Secrets).

---

## Verifying It Works

After a successful cycle you should see:

1. New commit: `📊 cycle #1 +$0.0000 Xs`
2. `status.json` updated with `total_runs: 1`
3. `docs/index.html` regenerated
4. (if evolution ran) commit: `🧬 evolve vX.Y.Z: ...`

If no earning actions ran, check the workflow log for the hint message listing which secrets to add.
