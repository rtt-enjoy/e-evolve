# Setup Guide

## Minimum Setup (5 minutes)

### 1. Fork the repo

Keep it public — required for free GitHub Pages and free Actions minutes.

### 2. Add one LLM secret

Repo → Settings → Secrets and variables → Actions → **New repository secret**

| Secret               | Source                                                        | Cost                          |
|----------------------|---------------------------------------------------------------|-------------------------------|
| `GLM_API_KEY`        | [z.ai](https://z.ai/manage-apikey/apikey-list) or [bigmodel.cn](https://open.bigmodel.cn) | **Main engine** — see below   |
| `ATRIA_API_KEY`      | [intern-ai.org.cn](https://discovery.intern-ai.org.cn)        | Free — first fallback         |
| `OPENROUTER_API_KEY` | [openrouter.ai](https://openrouter.ai/keys)                   | Free — second fallback        |
| `GROQ_API_KEY`       | [console.groq.com](https://console.groq.com)                  | Free                          |
| `GEMINI_API_KEY`     | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Free tier                     |
| `CEREBRAS_API_KEY`   | [cloud.cerebras.ai](https://cloud.cerebras.ai/)               | Free tier                     |
| `ANTHROPIC_API_KEY`  | [console.anthropic.com](https://console.anthropic.com)        | Paid                          |

Only one is required, but set `GLM_API_KEY`, `ATRIA_API_KEY` **and**
`OPENROUTER_API_KEY`.

**Main AI engine: GLM (`GLM_API_KEY`, Z.ai / Zhipu).** Every role tries it
first: evolution proposals (`upgrade`), research (`research`), and article and
newsletter drafting (`post`). If GLM cannot serve, **Atria** takes over, and if
Atria cannot either, the free **OpenRouter** chain does.

Z.ai and bigmodel.cn issue separate keys for the general API and the Coding
Plan, and those keys are not interchangeable. So the first GLM call of each
cycle sends a one-word probe to these hosts in order and keeps the first that
accepts the key:

1. `https://api.z.ai/api/coding/paas/v4` (Coding Plan, flat fee)
2. `https://api.z.ai/api/paas/v4` (general API, metered)
3. `https://open.bigmodel.cn/api/coding/paas/v4`
4. `https://open.bigmodel.cn/api/paas/v4`

Models are tried strongest first: `glm-5.2`, `glm-5.1`, `glm-5`, `glm-4.7`,
then the free `glm-4.7-flash` and `glm-4.5-flash`. A key with no balance
(code 1113) or a plan without a model (1311) steps down to the next one, so a
general-API key with no credit still lands on a free Flash model. `glm-5.3` is
left out because its thinking cannot be disabled. Every request sends
`thinking: disabled`, because reasoning tokens count against `max_tokens`.

**Cost:** on a metered general-API key with a balance, `glm-5.2` bills per
token (about $1.4 in / $4.4 out per 1M). A Coding Plan key bills nothing extra.
A key with no balance runs on the free Flash models.

GLM is switched off for the rest of the cycle on a rejected key, a spent
quota or usage limit, or two timeouts/outages. A rate limit (1302/1305) or a
refused request (prompt too long, flagged content) skips GLM for that one call
only. The Engine panel's **GLM** card shows the model and endpoint the probe
settled on, how many calls GLM answered, and why it fell back. Its last row
reports Atria. The sidebar pill reads `GLM live`, `GLM fallback`, or
`GLM not reported`.

**Atria (first fallback): `Atria-Dawn`, roughly 1B free tokens.**
It is called through the OpenAI-style endpoint
`https://discovery-api.intern-ai.org.cn/v1` with model `Atria-Dawn`.
Create the key at [discovery.intern-ai.org.cn](https://discovery.intern-ai.org.cn)
→ System Settings → API Key → Key Management
([docs](https://discovery.intern-ai.org.cn/docs/en/userCenter/api-key/)).
A key allows 500 requests/minute and **expires after 6 months** — an expired
key answers 401, so Atria quietly drops to the fallback (`auth_failed` on the
Engine panel). Rotate it before then.
When GLM is unavailable, `bot/llm.py` sends each role to Atria next. On a
401, a 404, or a quota-spent 429, Atria is switched off for the
rest of that cycle and each role falls through to its own zero-cost
OpenRouter chain (led by the `openrouter/free` auto-router), so a spent quota
never fails a cycle. A per-minute 429 that sends `Retry-After` only skips
Atria for that one call.

**Without `GLM_API_KEY` GLM is skipped** and Atria leads; without both, every
role runs on the OpenRouter fallback. The Engine panel then shows the roles as
`fallback`, not `active`. The card reflects the last completed cycle, so it
updates about an hour after you add a secret.

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

`bot/llm.py` automatically steps down from GLM to Atria, then to the
OpenRouter free-model chain, and then to the next configured provider on rate
limits. Adding any of these only increases headroom. It never changes routing
while GLM has capacity.

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
   one article per day, published in the morning window (default 06:00-12:00 UTC+9, set in `config/strategy.json` under `articles`). Omit it to keep the bot research-only.
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
