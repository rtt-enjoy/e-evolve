# Environment Keys

Use these names in local `.env` files and GitHub Actions repository secrets or
variables. Store real values only in `.env` or GitHub settings; committed files
should document names, never secret values.

## Required

Set at least one LLM provider key for LLM-backed runs:

| Key                  | Required    | Used by                         | Notes                            |
|----------------------|-------------|---------------------------------|----------------------------------|
| `GLM_API_KEY`        | One LLM key | `bot/llm.py`, feature readiness | **Main engine** for every role (Z.ai / Zhipu GLM, `glm-5.2` stepping down to the free `glm-4.7-flash`). The first call probes the Coding Plan and general hosts on api.z.ai and open.bigmodel.cn. Falls through to Atria on a rejected key, spent quota, or two timeouts. |
| `ATRIA_API_KEY`      | One LLM key | `bot/llm.py`, feature readiness | First fallback for every role (`Atria-Dawn`, ~1B free tokens). Falls through to OpenRouter on auth failure, missing model, or spent quota. |
| `GROQ_API_KEY`       | One LLM key | `bot/llm.py`, feature readiness | Free-tier friendly LLM provider. |
| `GEMINI_API_KEY`     | One LLM key | `bot/llm.py`, feature readiness | Free-tier friendly LLM provider; highest daily request ceiling of the free options. |
| `OPENROUTER_API_KEY` | One LLM key | `bot/llm.py`, feature readiness | Second fallback, after GLM and Atria; free-model chain per role. Free (`:free`) models are capped at 50 requests/day unless the account has ever purchased $10 in credits (then 1,000/day) -- verify current limit. |
| `ANTHROPIC_API_KEY`  | One LLM key | `bot/llm.py`, feature readiness | Higher-quality paid provider.    |
| `CEREBRAS_API_KEY`   | Optional    | `bot/llm.py`, feature readiness | Free-tier fallback: roughly 1M tokens/day, 14,400 requests/day per model, no credit card -- verify current limit. |

Provider selection prefers GLM, then Atria, then OpenRouter, then Anthropic/Gemini/Cerebras/Groq,
according to the role routing in `bot/llm.py`.

## Local and GitHub Metadata

| Key                         | Required                                     | Used by                                   | Notes                                                                                                |
|-----------------------------|----------------------------------------------|-------------------------------------------|------------------------------------------------------------------------------------------------------|
| `GITHUB_REPO`               | Optional locally                             | commands, dashboard, secret checks        | Repository slug such as `owner/repo`; workflow sets this from `github.repository`.                   |
| `GITHUB_REPOSITORY`         | Provided by GitHub Actions                   | secret checks                             | GitHub's built-in repository slug.                                                                   |
| `GH_TOKEN`                  | Optional locally                             | commands, secret checks                   | Token for GitHub Issues commands and configured-secret name lookup.                                  |
| `GITHUB_TOKEN`              | Provided by GitHub Actions, optional locally | commands, code-tech search, secret checks | GitHub Actions provides this automatically.                                                          |
| `GITHUB_ACTIONS`            | Provided by GitHub Actions                   | secret checks                             | Used to detect CI.                                                                                   |
| `GITHUB_CONFIGURED_SECRETS` | Optional locally                             | secret checks                             | Comma, space, or newline separated secret names for readiness checks when API lookup is unavailable. |

## Runtime Controls

| Key                            | Required | Used by                                    | Notes                                                                                              |
|--------------------------------|----------|--------------------------------------------|----------------------------------------------------------------------------------------------------|
| `CODE_TECH_EARN_ENABLED`       | Optional | `bot/main.py`, `bot/earning/code_techs.py` | Default is enabled. Set to `0`, `false`, `no`, or `off` to disable code-tech opportunity research. |

## Read-Only Status Context

| Key                   | Required | Used by         | Notes                                                                       |
|-----------------------|----------|-----------------|-----------------------------------------------------------------------------|
| `USDT_WALLET_ADDRESS` | Optional | `bot/status.py` | **Receive** address. Its live on-chain balance is the only figure the dashboard reports as earned. Never used to send. |
| `ETHERSCAN_API_KEY`   | Optional | `bot/status.py` | Improves Etherscan balance checks; free fallback token is used when absent. |

## Legacy Action Credentials

`DEV_TO_API_KEY` is **active**: when set, the bot drafts and publishes one
article per day to dev.to. It is the only outbound publishing key the bot uses.

| Key                | Required | Used by  | Notes                                              |
|--------------------|----------|----------|----------------------------------------------------|
| `DEV_TO_API_KEY`   | Optional | articles | dev.to API key. Without it the module skips.       |

Social posting, trading, minting, and payouts are blocked by policy, and the
modules that implemented them have been removed from the tree. No secrets exist
for them, and `.github/workflows/evolve.yml` no longer exports any.

## Workflow-Only Mapping

`.github/workflows/evolve.yml` maps GitHub Actions secrets with these same names
into the bot process. Do not commit a real `.env`; it is ignored by git. Update
`.env.example` and this page together whenever a new environment key is added.
