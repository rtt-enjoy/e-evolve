# Required GitHub Secrets

This document lists the GitHub repository secrets required for the E‑Evolve bot to operate.

## Secrets

| Secret | Description | Example |
|--------|-------------|---------|
| `ATRIA_API_KEY` | Atria LLM provider API key | `atria-...` |
| `GEMINI_API_KEY` | Gemini LLM provider API key | `AIza...` |
| `GH_TOKEN` | GitHub token for API access | `ghp_...` |
| `GROQ_API_KEY` | Groq LLM provider API key | `gsk_...` |
| `OPENROUTER_API_KEY` | OpenRouter LLM provider API key | `sk-or-...` |
| `USDT_WALLET_ADDRESS` | Tron TRC‑20 USDT receive address | `TFTNsf...` |
| `CEREBRAS_API_KEY` | Cerebras Cloud free‑tier API key | `cb-...` |
| `DEV_TO_API_KEY` | dev.to API key for publishing | `abc123...` |

## How to Add a Secret

1. Navigate to your GitHub repository.
2. Click **Settings** → **Secrets and variables** → **Actions**.
3. Click **New repository secret**.
4. Enter the secret name (e.g., `ATRIA_API_KEY`).
5. Paste the API key or value in the secret value field.
6. Click **Add secret**.

## Notes

- All secrets are stored securely and are not shared publicly.
- The bot reads these secrets from the environment at runtime.
- If a secret is missing, the corresponding feature will be skipped.