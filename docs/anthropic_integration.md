# Enable Anthropic LLM Fallback

E-Evolve can use Anthropic as a backup LLM provider to avoid downtime if
Gemini, OpenRouter, or Groq are unavailable.

## Steps to activate

1. Create an Anthropic account at https://console.anthropic.com.
2. Generate an API key in the **API Keys** section.
3. Add `ANTHROPIC_API_KEY` as a GitHub Actions secret in the repository
   settings under **Secrets and variables → Actions**.
4. Restart the workflow (or wait for the next scheduled run) to load the
   new secret.