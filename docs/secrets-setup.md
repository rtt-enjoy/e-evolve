# Secret Setup Guide

This document lists the GitHub secrets required for the E-Evolve bot to operate at full capacity.

## Required Secrets

### Anthropic API Key (Claude LLM)

- **Purpose**: Enables the `llm_anthropic` feature for research and article drafting.
- **How to obtain**:
  1. Go to [Anthropic Console](https://console.anthropic.com/settings/keys) and create a new API key.
  2. Copy the generated key.
  3. In your GitHub repository, navigate to **Settings → Secrets and variables → Actions**.
  4. Click **New repository secret**, name it `ANTHROPIC_API_KEY`, and paste the key.

### Cerebras API Key (Free Tier LLM)

- **Purpose**: Provides high‑volume free AI for research and article drafting.
- **How to obtain**:
  1. Visit [Cerebras Cloud](https://cloud.cerebras.ai/) and create a free account (no credit‑card required).
  2. Generate an API key in the Cerebras dashboard.
  3. Add it as a GitHub secret named `CEREBRAS_API_KEY`.

## Already Configured Secrets

The following secrets are already present in this repository (as shown in `bot/dashboard.py`):

- `GEMINI_API_KEY`
- `GROQ_API_KEY`
- `OPENROUTER_API_KEY`
- `USDT_WALLET_ADDRESS`

## Optional: Test the USDT Wallet on Testnet

If you want to verify that the on‑chain payout pipeline works before using real funds:

1. Obtain testnet TRX and testnet USDT from a faucet such as [tronfaucet.com](https://tronfaucet.com/).
2. Send a small test USDT transfer to the wallet address stored in `USDT_WALLET_ADDRESS`.
3. Run `receipt_check` (or the bot’s status phase) to confirm the balance is detected and the footer appears on published articles.

## Notes

- Secrets are **repository‑level**; they are not shared with any third party.
- The bot reads secrets at runtime, so a restart is not required after adding a new secret.
- If a feature remains inactive after adding the secret, double‑check the secret name spelling and that the key has not expired.

---

*Last updated: 2026‑09‑20*