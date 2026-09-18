# Adding LLM API Keys for E-Evolve

To enable additional LLM providers for increased resilience and free tier usage, add the following secrets to your GitHub repository:

## Anthropic (Claude)
1. Go to https://console.anthropic.com/ and sign in or create an account
2. Navigate to API Keys and create a new key
3. Copy the key and add it as a GitHub secret named `ANTHROPIC_API_KEY`

## Cerebras
1. Go to https://cloud.cerebras.ai/ and sign up for a free account
2. Generate an API key from the dashboard
3. Add it as a GitHub secret named `CEREBRAS_API_KEY`

Once added, the bot will automatically detect and use these keys in the next cycle.