# Environment Keys

Use these names in local `.env` files and GitHub Actions repository secrets or
variables. Store real values only in `.env` or GitHub settings; committed files
should document names, never secret values.

## Required

Set at least one LLM provider key for LLM-backed runs:

| Key | Required | Used by | Notes |
|-----|----------|---------|-------|
| `GROQ_API_KEY` | One LLM key | `bot/llm.py`, feature readiness | Free-tier friendly LLM provider. |
| `GEMINI_API_KEY` | One LLM key | `bot/llm.py`, feature readiness | Free-tier friendly LLM provider. |
| `OPENROUTER_API_KEY` | One LLM key | `bot/llm.py`, feature readiness | Free-model fallback option. |
| `ANTHROPIC_API_KEY` | One LLM key | `bot/llm.py`, feature readiness | Higher-quality paid provider. |

Provider selection prefers Anthropic when present, then Gemini/OpenRouter/Groq
according to the role routing in `bot/llm.py`.

## Local and GitHub Metadata

| Key | Required | Used by | Notes |
|-----|----------|---------|-------|
| `GITHUB_REPO` | Optional locally | commands, dashboard, secret checks | Repository slug such as `owner/repo`; workflow sets this from `github.repository`. |
| `GITHUB_REPOSITORY` | Provided by GitHub Actions | secret checks | GitHub's built-in repository slug. |
| `GH_TOKEN` | Optional locally | commands, secret checks | Token for GitHub Issues commands and configured-secret name lookup. |
| `GITHUB_TOKEN` | Provided by GitHub Actions, optional locally | commands, code-tech search, secret checks | GitHub Actions provides this automatically. |
| `GITHUB_ACTIONS` | Provided by GitHub Actions | secret checks | Used to detect CI. |
| `GITHUB_CONFIGURED_SECRETS` | Optional locally | secret checks | Comma, space, or newline separated secret names for readiness checks when API lookup is unavailable. |

## Runtime Controls

| Key | Required | Used by | Notes |
|-----|----------|---------|-------|
| `CLAUDE_CLI_MODE` | Optional | `bot/llm.py` | Set to `1` only when using an installed, authenticated Claude CLI locally. |
| `CODE_TECH_EARN_ENABLED` | Optional | `bot/main.py`, `bot/earning/code_techs.py` | Default is enabled. Set to `0`, `false`, `no`, or `off` to disable code-tech opportunity research. |
| `VITE_ENABLE_OFFLINE_AGENT_UI` | Optional | `frontend/vite.config.ts` | Local dev shows offline tools by default; production builds show them only when set to `1`. |
| `EARN_CTA_URL` | Optional | `bot/earning/twitter.py` | URL appended by legacy draft/social helpers. |
| `EARN_CTA_LABEL` | Optional | `bot/earning/twitter.py` | Human-readable label for `EARN_CTA_URL`; defaults to project-link text. |

## Read-Only Status Context

| Key | Required | Used by | Notes |
|-----|----------|---------|-------|
| `USDT_WALLET_ADDRESS` | Optional | `bot/status.py` | Enables wallet/status readiness and balance lookup. |
| `ETHERSCAN_API_KEY` | Optional | `bot/status.py` | Improves Etherscan balance checks; free fallback token is used when absent. |

## Legacy Action Credentials

These names are kept for setup readiness, suggestions, and legacy modules.
Current project policy treats them as research/setup context only: the bot must
not publish, post, trade, withdraw, mint, or comment externally from these keys.

| Key | Required | Legacy area | Notes |
|-----|----------|-------------|-------|
| `DEV_TO_API_KEY` | Optional | articles | dev.to API key. |
| `MEDIUM_INTEGRATION_TOKEN` | Optional | articles | Medium integration token. |
| `TWITTER_API_KEY` | Optional | Twitter/X | Consumer API key. |
| `TWITTER_API_SECRET` | Optional | Twitter/X | Consumer API secret. |
| `TWITTER_ACCESS_TOKEN` | Optional | Twitter/X | Access token. |
| `TWITTER_ACCESS_SECRET` | Optional | Twitter/X | Access token secret. |
| `BINANCE_API_KEY` | Optional | crypto/payout | Binance API key. |
| `BINANCE_SECRET_KEY` | Optional | crypto/payout | Binance secret key. |
| `BINANCE_WITHDRAW_ADDRESS` | Optional | payout | Destination address for legacy payout logic. |
| `ETH_PRIVATE_KEY` | Optional | NFT | Dedicated wallet private key. |
| `ETH_WALLET_ADDRESS` | Optional | NFT | Corresponding public wallet address. |
| `NFT_CONTRACT_ADDRESS` | Optional | NFT | Pre-deployed ERC-721 contract address. |
| `NFT_STORAGE_TOKEN` | Optional | NFT | nft.storage token for IPFS pinning. |

## Workflow-Only Mapping

`.github/workflows/evolve.yml` maps GitHub Actions secrets with these same names
into the bot process. Do not commit a real `.env`; it is ignored by git. Update
`.env.example` and this page together whenever a new environment key is added.
