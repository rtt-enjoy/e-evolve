# E-Evolve Bot Documentation

## Overview

E-Evolve is a GitHub Actions bot for RAG, online research, market analysis, and
earning suggestions. Code changes happen in Codex, not in the hourly bot.

## Runtime Policy

Allowed API-key use:

- RAG and context retrieval
- online research
- market analysis
- earning suggestions
- draft-only text

Blocked API-key use:

- code updates
- article publishing
- social posting
- crypto trading or payouts
- NFT minting
- external issue comments

## Quick Start

1. Clone the repository.
2. Install dependencies with `pip install -r requirements.txt`.
3. Add one LLM key, such as `GROQ_API_KEY`, `GEMINI_API_KEY`, or `OPENROUTER_API_KEY`.
4. Run `python -m bot.main` locally when LLM keys are available.

## Features

- Code-tech research queue with ranked suggestions.
- LLM routing for research and draft-only suggestion text.
- Static dashboard published under `docs/`.

## Development

Run local verification before committing prompt-driven changes. The dashboard is
built from `frontend/` into `docs/`.
