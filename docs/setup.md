# Setup Guide

## Minimum Setup (5 minutes)

### 1. Fork the repo

Keep it public — required for free GitHub Pages and free Actions minutes.

### 2. Add one LLM secret

Repo → Settings → Secrets and variables → Actions → **New repository secret**

| Secret               | Source                                                        | Cost                          |
|----------------------|---------------------------------------------------------------|-------------------------------|
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai/keys)                   | **Main engine** — see below   |
| `GROQ_API_KEY`       | [console.groq.com](https://console.groq.com)                  | Free                          |
| `GEMINI_API_KEY`     | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Free tier                     |
| `CEREBRAS_API_KEY`   | [cloud.cerebras.ai](https://cloud.cerebras.ai/)               | Free tier                     |
| `ANTHROPIC_API_KEY`  | [console.anthropic.com](https://console.anthropic.com)        | Paid                          |

Only one is required.

**Main AI engine: free OpenRouter models, no credits required.** `bot/llm.py`
routes every role through a zero-cost OpenRouter model chain — `openai/gpt-oss-20b:free`
by default, `nvidia/nemotron-3-ultra-550b-a55b:free` for research (long
context, strongest reasoning), stepping down through more free models on
429/rate-limit before ever failing a cycle. No OpenRouter credits are needed.

**Know the daily ceiling.** OpenRouter's free (`:free`) models are capped at
20 requests/minute and only **50 requests/day** unless the account has ever
purchased $10 in credits (then 1,000/day) — verify the current limit at
[openrouter.ai/docs](https://openrouter.ai/docs/api-reference/limits). An
hourly bot making multiple LLM calls per cycle can approach that ceiling, so
add at least one fallback key:

- `GEMINI_API_KEY` — free tier, no card, roughly 1,500 requests/day on
  Gemini 2.5 Flash (verify current limit).
- `CEREBRAS_API_KEY` — free tier, no card, roughly 1M tokens/day and 14,400
  requests/day per model (verify current limit).
- `GROQ_API_KEY` — free tier, no card, fast inference.

`bot/llm.py` automatically steps down through the OpenRouter free-model chain
and then falls back to the next configured provider on rate limits, so adding
any of these only increases headroom — it never changes routing when
OpenRouter has capacity.

Use the same variable names in both places:

- Local development: copy `.env.example` to `.env`, then fill in private values.
- GitHub Actions: add repository secrets with matching names, such as `GROQ_API_KEY`.

`.env` is ignored by git and should never be committed. `.env.example` is the
committed template and must contain names only, not real secret values.

The full environment key reference is in [`docs/environment.md`](environment.md).

### No-ID free self-earn path

Use this order when you cannot use Binance identity verification, phone-gated
social APIs, Claude premium features, paid LLM accounts, or funded wallets:

1. Free-AI earning leads - enabled by default and no external secret required.
2. `GROQ_API_KEY` or `GEMINI_API_KEY` - free LLM generation within rate limits.
3. `OPENROUTER_API_KEY` with no credits - still works, using free models only.

These keys no longer activate runtime actions:

1. `DEV_TO_API_KEY` — **active**. Enables live article publishing to dev.to,
   one article per day. Omit it to keep the bot research-only.
2. Twitter/X posting keys.
3. Binance trading or payout keys.
4. Ethereum NFT minting keys.

Keys 2-4 are setup context only. The bot must not post socially, trade,
withdraw, mint, or comment on external issues.

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

| Secret             | Source                         |
|--------------------|--------------------------------|
| `DEV_TO_API_KEY`   | dev.to → Settings → Extensions |

This is the only publishing secret. Without it the articles module skips
silently and the cycle still succeeds.

### Read-only wallet balance (optional)

| Secret                | Notes                                                  |
|-----------------------|--------------------------------------------------------|
| `USDT_WALLET_ADDRESS` | Receive address. Reported read-only on the dashboard.  |
| `ETHERSCAN_API_KEY`   | Optional, improves ERC-20 balance lookup reliability.  |

There is no withdrawal or transfer code path anywhere in the tree.

### Removed capabilities

Social posting, crypto trading, NFT minting, and payouts are blocked by policy.
The modules that implemented them have been deleted, so there is nothing to
configure and no secret to add.

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
