# Setup Guide

## Minimum Setup (5 minutes)

### 1. Fork the repo

Keep it public — required for free GitHub Pages and free Actions minutes.

### 2. Add one LLM secret

Repo → Settings → Secrets and variables → Actions → **New repository secret**

| Secret | Source | Cost |
|--------|--------|------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | Free |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Free tier |
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai/keys) | Free models available |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Paid (higher quality) |

Only one is required. If you have no budget or cannot use premium LLM features,
start with `GROQ_API_KEY` or `GEMINI_API_KEY` and add `DEV_TO_API_KEY` for the
first earning module.

### No-ID free self-earn path

Use this order when you cannot use Binance identity verification, phone-gated
social APIs, Claude premium features, paid LLM accounts, or funded wallets:

1. Code-tech leads - enabled by default and no external secret required.
2. `GROQ_API_KEY` or `GEMINI_API_KEY` - free LLM generation within rate limits.
3. Optional `OPENROUTER_API_KEY` - only for free models if the first two are not enough.
4. `DEV_TO_API_KEY` - free article publishing.
5. Optional GitHub Actions variable `EARN_CTA_URL` - your sponsor, tip,
   newsletter, affiliate, portfolio, or product link appended to each article.
6. Optional variable `EARN_CTA_LABEL` - link text for that CTA.

Avoid these until you explicitly choose the tradeoff:

1. Binance trading or payout - exchange identity verification and funded balance.
2. Claude/Anthropic premium path - paid access.
3. Twitter/X API posting - can require phone-gated or paid developer access.
4. Ethereum NFT minting - wallet funding, contracts, and gas.

More detail: [`docs/no-id-free-path.md`](no-id-free-path.md).

With `EARN_CTA_URL` configured, the article module periodically selects buyer-intent
topics from `config/strategy.json`. Tune `articles.buyer_intent_ratio` lower for more
general audience growth or higher for more conversion-focused publishing.

Leave crypto and NFT modules off until you have money you can afford to risk.

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
| `BINANCE_API_KEY` | Enable Spot trading only unless you intentionally enable auto-payout |
| `BINANCE_SECRET_KEY` | " |
| `BINANCE_WITHDRAW_ADDRESS` | Optional Exodus receive address for auto-payout |

> **Warning:** Start with a small balance. LLM-driven trading is not guaranteed to be profitable.

For Exodus payouts, the default strategy withdraws `USDT` on `BSC` to match an
Exodus BNB Smart Chain receive address. In Exodus, copy the receive address for
the same network configured in `config/strategy.json`, then whitelist that exact
address and network in Binance before enabling API withdrawals. The payout guard
also accepts `ETH` addresses that start with `0x` and `TRX` addresses that start
with `T`, but the configured network and Exodus receive network must match.

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

GitHub does not allow secret values to be downloaded after they are saved. For
local diagnostics, set `GH_TOKEN` or `GITHUB_TOKEN` with repo metadata access and
run:

```bash
python -m bot.github_secrets
```

That prints configured GitHub Actions secret names only, never values. Local
cycles still need real values in `.env` before modules can call external APIs,
but the dashboard readiness check will use the online names when a token is
available.

---

## Verifying It Works

After a successful cycle you should see:

1. New commit: `📊 cycle #1 +$0.0000 Xs`
2. `status.json` updated with `total_runs: 1`
3. `docs/index.html` regenerated
4. (if evolution ran) commit: `🧬 evolve vX.Y.Z: ...`

If no earning actions ran, check the workflow log for the hint message listing which secrets to add.
