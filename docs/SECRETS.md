# Required GitHub Secrets

This project uses several external API keys and wallet addresses to operate. Add them as repository secrets in GitHub Settings → Secrets and variables → Actions.

| Secret Name | Purpose | Example Value |
|-------------|---------|---------------|
| ATRIA_API_KEY | Atria LLM provider | sk-ant-... |
| GEMINI_API_KEY | Gemini LLM provider | AI... |
| OPENROUTER_API_KEY | OpenRouter LLM provider | sk-openrouter-... |
| GROQ_API_KEY | Groq LLM provider | gsk-... |
| DEV_TO_API_KEY | dev.to publishing API | abc123... |
| USDT_WALLET_ADDRESS | TRC-20 USDT receive address | TFTNsf... |
| ANTHROPIC_API_KEY | Anthropic LLM provider (free-tier Haiku) | sk-ant-... |
| CEREBRAS_API_KEY | Cerebras Cloud LLM provider (free tier) | cb-... |

## How to Add a Secret

1. Navigate to your GitHub repository.
2. Click **Settings** → **Secrets and variables** → **Actions**.
3. Click **New repository secret**.
4. In **Name**, paste the secret name exactly as shown above.
5. In **Secret**, paste the API key or wallet address.
6. Click **Add secret**.

After adding all required secrets, the bot will have access to all active providers and can publish articles, run earning modules, and process on‑chain tips.

We also note that **GH_TOKEN** is already configured and does not need to be added.