# E-Evolve

A self-improving GitHub Actions bot that researches, writes, and publishes technical articles to dev.to while building passive income streams through crypto-native monetization.

## What it does

- **Daily articles**: Publishes one original technical article per day to dev.to, written from real trending sources
- **Follow-up posts**: Mines high-performing articles for deeper sequels that compound reach
- **Backfill**: Adds support footers to previously published articles so existing readers can contribute
- **Earning research**: Maintains a ranked queue of zero-budget passive income channels (code_techs) and recurring-revenue ideas (mrr_ideas)
- **Wallet monitoring**: Tracks on-chain USDT balance on Tron (TRC-20) for verified earnings

## Architecture

```
.github/workflows/bot.yml   # Hourly GitHub Actions schedule
bot/main.py                 # Orchestrator: loads status, runs products, writes status
bot/earning/                # Product modules (articles, newsletter, backfill, code_techs, mrr_ideas)
bot/llm.py                  # Multi-provider LLM client (OpenRouter, Gemini, Groq, Anthropic, Cerebras)
config/strategy.json        # All tunable parameters (no code changes needed)
docs/status.json            # Public dashboard data (deployed to GitHub Pages)
frontend/                   # React dashboard (Vite → docs/)
```

## Active products

| Product | Purpose | Output |
|---------|---------|--------|
| `articles` | Daily dev.to article from trending source | 1 article/day |
| `newsletter` | Weekly digest of curated stories | 1 digest/week |
| `backfill` | Adds wallet footer to old posts | Updates existing posts |
| `code_techs` | Research: zero-budget passive income channels | Ranked queue in status.json |
| `mrr_ideas` | Research: recurring-revenue models fitting this stack | Triage in status.json |

## Required secrets

| Secret | Purpose | Required |
|--------|---------|----------|
| `DEV_TO_API_KEY` | Publish to dev.to | Yes |
| `OPENROUTER_API_KEY` | Primary LLM provider (free tier) | Yes |
| `GEMINI_API_KEY` | Fallback LLM provider | No |
| `GROQ_API_KEY` | Fallback LLM provider | No |
| `ANTHROPIC_API_KEY` | Fallback LLM provider | No |
| `CEREBRAS_API_KEY` | Fallback LLM provider | No |
| `USDT_WALLET_ADDRESS` | Tron (TRC-20) receive address for tips | Yes |
| `GH_TOKEN` | GitHub API (for repo stats, releasing) | Yes |

## Configuration

All tunable parameters live in `config/strategy.json`. Key sections:

```json
{
  "articles": {
    "max_articles_per_cycle": 1,
    "source_max_age_hours": 24,
    "followup_enabled": true,
    "followup_min_views": 40
  },
  "backfill": {
    "enabled": true,
    "max_per_cycle": 10
  },
  "code_techs": {
    "enabled": true,
    "refresh_hours": 6,
    "daily_target_usd": 10.0
  },
  "mrr_ideas": {
    "enabled": true,
    "refresh_hours": 48,
    "min_score": 50
  },
  "payout": {
    "enabled": true,
    "network": "TRC-20",
    "address": "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"
  }
}
```

## Local development

```bash
# Install Python deps
pip install -r requirements.txt

# Run one cycle (requires secrets in env)
python -m bot.main

# Build dashboard
cd frontend && npm install && npm run build
```

## Dashboard

The live dashboard is at: https://<owner>.github.io/<repo>/

It reads `docs/status.json` which is committed every cycle. The React app shows:
- Wallet balance and earnings log
- Article performance and archetype analysis
- Code-techs opportunity queue
- MRR idea triage
- System health and secrets status

## Passive income strategy

This project follows the **Passive Income Doctrine** (`docs/passive-income-doctrine.md`):

1. **Zero marginal cost per user** — client-side code, free hosting, free scheduler
2. **Receive path on the artifact** — wallet address in article footer, README, FUNDING.yml
3. **Free channels first** — list on zero-cost storefronts before paying for discovery
4. **Measure only on-chain** — listings and views are not revenue
5. **No owner hours for sale** — freelance/consulting is a job, not passive income

## Support this work

These write-ups are researched and published with no paywall, sponsor, or tracking. If one saved you an afternoon, a small tip keeps them coming.

**USDT / USDC / USDD on Tron (TRC-20)**

```
TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
```

Or scan the QR code in the dashboard.

## License

MIT — see LICENSE file.