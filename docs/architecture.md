# Architecture

## Cycle Execution

```
bot/main.py (entry: python -m bot.main)
|
|- Phase 0: LLMClient()          bot/llm.py
|- Phase 1: status.load()        bot/status.py
|- Phase 2: commands.read()      bot/commands.py
|- Phase 3: evolution skip       Codex owns code changes
|- Phase 4: research modules     bot/earning/code_techs.py
`- Phase 5: state update         status/dashboard/git commit
```

## Operating Policy

API keys are limited to:

- RAG and context retrieval
- online research
- market analysis
- earning suggestions
- draft-only text

API keys must not be used for:

- code changes
- article publishing
- social posting
- trading or payouts
- NFT minting
- external issue comments

## Data Flow

```
GitHub Secrets / env vars
    -> status.py detects LLM and read-only features
    -> llm.py routes research and draft calls
    -> code_techs.py refreshes ranked suggestions
    -> dashboard.py publishes safe public status data
```

`bot/evolution.py` remains as legacy reference code, but `bot/main.py` does not
call it. Prompt-driven code updates are made here in Codex, verified locally,
then committed and pushed.
