# LLM Providers

This project can use several free-tier LLM providers for research and drafting. The bot picks the first one whose API key is present in the GitHub secrets.

## Provider order

1. **Gemini** (`GEMINI_API_KEY`) — Google AI Studio. No credit card required. Gemini 2.5 Flash free tier is roughly 1,500 requests/day.
2. **OpenRouter** (`OPENROUTER_API_KEY`) — free `:free` models. Capped at 20 req/min and 50 req/day unless the account has purchased $10 in credits (then 1,000/day).
3. **Groq** (`GROQ_API_KEY`) — fast inference, generous free tier.
4. **Cerebras** (`CEREBRAS_API_KEY`) — no credit card required. Roughly 1M tokens/day and 14,400 requests/day per model.
5. **Anthropic** (`ANTHROPIC_API_KEY`) — Claude. Usage may incur charges after trial credits; a standing free tier is not guaranteed.

## Adding a key

1. Create an account with the provider.
2. Generate an API key.
3. Add it as a GitHub secret with the exact name above.

The bot reads keys at startup and falls back to the next provider in the list if a call fails. No code change is needed to switch providers.