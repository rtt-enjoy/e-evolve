# E‑Evolve Bot Documentation

## Overview
E‑Evolve is a self‑improving GitHub Actions bot that can earn USD by publishing articles, trading crypto, minting NFTs, and posting Twitter threads.

## Activation Guide for Optional Features

### 1. Twitter (X) Threads
- **Required secrets**: `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`
- Add them in **Settings → Secrets and variables → Actions**.
- The bot will automatically start generating and posting threads once the secrets are present.

### 2. Binance Crypto Trading
- **Required secrets**: `BINANCE_API_KEY`, `BINANCE_SECRET_KEY`
- (Optional) configure trading parameters in `config/strategy.json` under the `crypto` key.
- After adding the secrets, the `crypto` module will run each cycle.

### 3. NFT Minting (Ethereum)
- **Required secrets**: `ETH_PRIVATE_KEY`, `ETH_WALLET_ADDRESS`, `NFT_CONTRACT_ADDRESS`
- (Optional) `NFT_STORAGE_TOKEN` to pin metadata on IPFS via nft.storage.
- Deploy an ERC‑721 contract first, then add its address as a secret.

### 4. Medium Articles
- **Required secret**: `MEDIUM_INTEGRATION_TOKEN`
- Add the token to enable publishing to Medium in addition to dev.to.

### 5. Anthropic LLM (currently inactive)
- **Required secret**: `ANTHROPIC_API_KEY`
- Add the key to switch the LLM provider to Anthropic.

## General Steps
1. Add the necessary secrets for the features you want to enable.
2. Ensure `requirements.txt` includes the needed packages (the bot will install them on the next run).
3. Commit any changes; the next workflow execution will pick up the new configuration.

---
*All optional features are safe to enable; they will only run when their required secrets are present.*