# Local TODO Needed

Created: 2026-06-04

## Why Local Fallback Was Used

- Online source research worked when network access was approved: the focused verifier fetched 33 leads from public sources.
- The configured research LLM route could not produce the online AI brief because the active API key returned an authentication error.
- Codex completed the implementation locally to preserve quality, while keeping the runtime policy research-only.

## Needed To Restore Full Online AI Quality

1. Refresh the free/low-cost research LLM secret used by the bot, preferably `OPENROUTER_API_KEY` for free-model research routing.
2. Re-run `python -m bot.main` or wait for the next GitHub Actions cycle.
3. Confirm `docs/code-tech-opportunities.md` includes an `Online AI Brief` generated from fresh online leads.
4. If the online brief succeeds, remove this file in a follow-up commit.
