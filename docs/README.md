# E-Evolve

Autonomous evolution engine for self-improving GitHub Actions bot.

## Overview

E-Evolve is a self-improving bot that runs on GitHub Actions. It researches, writes, and publishes technical articles to dev.to, maintains a passive income research queue, and evolves its own codebase through automated pull requests.

## Features

- **Daily Articles**: Publishes one original technical article per day to dev.to
- **Weekly Newsletter**: Curates and publishes a weekly digest
- **Backfill System**: Adds support footers to previously published articles
- **Code Techs Queue**: Researches zero-budget passive income opportunities for digital products
- **MRR Ideas**: Triages recurring revenue models against hard constraints
- **Wallet Integration**: USDT (TRC-20) receive address published in every article footer
- **Multi-LLM Support**: OpenRouter, Gemini, Groq, with fallback support for Anthropic and Cerebras

## Quick Start

1. Fork this repository
2. Add required GitHub secrets:
   - `DEV_TO_API_KEY` - for publishing articles
   - `OPENROUTER_API_KEY` - primary LLM provider
   - `GEMINI_API_KEY` - fallback LLM provider
   - `GROQ_API_KEY` - fallback LLM provider
   - `USDT_WALLET_ADDRESS` - Tron (TRC-20) receive address for tips
   - `GH_TOKEN` - GitHub token with repo scope (auto-provided)
3. Enable GitHub Actions
4. The bot runs hourly via scheduled workflow

## Optional Secrets

- `ANTHROPIC_API_KEY` - activates Anthropic LLM route (free tier available)
- `CEREBRAS_API_KEY` - activates Cerebras LLM route (free tier available)

## Support This Work

These write-ups are researched and published with no paywall, sponsor, or tracking. If one saved you an afternoon, a small tip keeps them coming.

**USDT (TRC-20)**: `TFTNsfyomKrnUutRjBTGVULp19ByW29KbY`

## Dashboard

View the live dashboard at: https://github.com/<owner>/<repo>/blob/main/docs/status.json

## Configuration

Edit `config/strategy.json` to adjust:
- Article publishing cadence and quality thresholds
- Backfill batch size
- Code techs refresh interval and scoring weights
- MRR idea triage criteria

## Architecture

```
bot/
├── main.py              # Orchestrator
├── evolution.py         # Self-improvement loop
├── llm.py               # Multi-provider LLM client
├── status.py            # State persistence & sanitization
├── dashboard.py         # GitHub Pages data publisher
├── commands.py          # Chat command handlers
├── git_utils.py         # Git operations
├── earnings.py          # Earnings aggregation
└── earning/
    ├── articles.py      # Daily dev.to articles
    ├── newsletter.py    # Weekly digest
    ├── backfill.py      # Footer backfill for old posts
    ├── code_techs.py    # Passive income opportunity queue
    ├── mrr_ideas.py     # Recurring revenue triage
    ├── devto.py         # dev.to publishing & gates
    ├── devto_stats.py   # Reach analytics
    ├── payout.py        # Wallet footer & address management
    ├── receipt_check.py # Footer verification
    ├── trending.py      # Source discovery
    ├── wallet_assets.py # On-chain balance check
    ├── attribution.py   # Revenue correlation
    └── _shared.py       # Config, cadence, parsing utilities
```

## License

MIT