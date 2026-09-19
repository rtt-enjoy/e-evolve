# GitHub Secrets Guide

This document describes every GitHub secret required by the E‑Evolve bot and how to add it.

## Required Secrets

| Secret Name | Provider | How to Obtain |
|-------------|----------|---------------|
| `ANTHROPIC_API_KEY` | Anthropic (Claude) | 1. Visit https://console.anthropic.com/ and sign in or create an account.<br>2. Navigate to **API Keys** → **Create new key**.<br>3. Copy the key and add it as a repository secret named `ANTHROPIC_API_KEY`. |
| `CEREBRAS_API_KEY` | Cerebras Cloud | 1. Go to https://cloud.cerebras.ai/ and sign up for a free account (no credit card required).<br>2. In the dashboard, click **API Keys** → **Generate key**.<br>3. Copy the key and add it as a repository secret named `CEREBRAS_API_KEY`. |
| `GEMINI_API_KEY` | Google AI Studio | 1. Open https://aistudio.google.com/app/apikey and sign in.<br>2. Click **Create API key**.<br>3. Copy the key and add it as a repository secret named `GEMINI_API_KEY`. |
| `GROQ_API_KEY` | Groq | 1. Visit https://console.groq.com/ and create an account.<br>2. Go to **API Keys** → **Create key**.<br>3. Copy the key and add it as a repository secret named `GROQ_API_KEY`. |
| `OPENROUTER_API_KEY` | OpenRouter | 1. Sign up at https://openrouter.ai/ and obtain an API key from the dashboard.<br>2. Copy the key and add it as a repository secret named `OPENROUTER_API_KEY`. |
| `USDT_WALLET_ADDRESS` | Tron (TRC‑20) | 1. Ensure you have a Tron wallet address that will receive tips.<br>2. Add the address (prefixed with `T`) as a repository secret named `USDT_WALLET_ADDRESS`. |
| `GH_TOKEN` | GitHub | 1. Generate a Personal Access Token at https://github.com/settings/tokens.<br>2. Select scopes: `repo` and `workflow`.<br>3. Copy the token and add it as a repository secret named `GH_TOKEN`. |

## Adding a Secret

1. Navigate to the repository on GitHub.
2. Click **Settings** → **Secrets and variables** → **Actions**.
3. Select **New repository secret**.
4. Enter the secret name exactly as shown in the table (case‑sensitive).
5. Paste the key/value and click **Add secret**.

## Why These Secrets Matter

- **LLM Providers**: Anthropic, Cerebras, Gemini, Groq, and OpenRouter power the bot's research, drafting, and upgrade workflows. A missing key simply de‑activates that provider; the bot falls back to the others.
- **Wallet**: The `USDT_WALLET_ADDRESS` is the destination for all on‑chain tips. Without it, the payout footer cannot be verified.
- **GitHub Token**: Required for internal API calls (e.g., updating article bodies) and for the bot to read repository metadata.

## Updating Secrets

If a key expires or you need to rotate it, repeat the steps above and replace the value in GitHub. The bot reads the secret at runtime, so no code changes are required.

## Troubleshooting

- **Secret not detected**: Ensure the secret name matches exactly, including case. Re‑run the bot's status check.
- **Provider errors**: Verify the key has the correct permissions and has not been revoked.
- **Rate limits**: Free tiers have daily caps; monitor usage in each provider's console.

---

*Last updated: 2026‑19*