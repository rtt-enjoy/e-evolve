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
start with `GROQ_API_KEY` or `GEMINI_API_KEY`. API keys are used for RAG,
research, market analysis, suggestions, and draft-only text.

Use the same variable names in both places:

- Local development: copy `.env.example` to `.env`, then fill in private values.
- GitHub Actions: add repository secrets with matching names, such as `GROQ_API_KEY`.

`.env` is ignored by git and should never be committed. `.env.example` is the
committed template and must contain names only, not real secret values.

The full environment key reference is in [`docs/environment.md`](environment.md).

### No-ID free self-earn path

Use this order when you cannot use Binance identity verification, phone-gated
social APIs, Claude premium features, paid LLM accounts, or funded wallets:

1. Code-tech leads - enabled by default and no external secret required.
2. `GROQ_API_KEY` or `GEMINI_API_KEY` - free LLM generation within rate limits.
3. Optional `OPENROUTER_API_KEY` - free-model research fallback.

These keys no longer activate runtime actions:

1. dev.to or Medium publishing keys.
2. Twitter/X posting keys.
3. Binance trading or payout keys.
4. Ethereum NFT minting keys.

If present, those keys are setup context only. The bot must not publish, post,
trade, withdraw, mint, or comment on external issues.

More detail: [`docs/no-id-free-path.md`](no-id-free-path.md).

### 3. Trigger first run

Actions tab → **evolve** → **Run workflow**

Watch the logs. A successful first run commits `status.json` and `docs/index.html`.

### 4. Enable GitHub Pages

Settings → Pages → Source: branch `main`, folder `/docs` → **Save**

Dashboard: `https://YOUR_USERNAME.github.io/e-evolve`

---

## Research Setup

No publishing, posting, trading, payout, or minting key is required. Keep runtime setup focused on LLM keys and the default code-tech research queue.

Legacy action-module notes below are intentionally not activation instructions.

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
cp .env.example .env
# Edit .env and set at least one of GROQ_API_KEY, GEMINI_API_KEY,
# OPENROUTER_API_KEY, or ANTHROPIC_API_KEY.

# 4. Run one cycle
python -m bot.main
```

`python-dotenv` loads `.env` automatically when running locally. CI does not use
`.env`; the workflow reads GitHub Actions repository secrets with the same names.

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
