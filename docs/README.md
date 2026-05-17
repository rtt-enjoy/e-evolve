# E‑Evolve Bot – Activation Guide

This repository contains an autonomous GitHub Actions bot that can earn money through several optional features. Below are the steps to enable each feature.

## 1. Medium Publishing (articles_medium)

1. Go to **https://medium.com/me/settings** and create an **Integration token** with the *Publishing* scope.
2. Add the token as a GitHub secret named `MEDIUM_INTEGRATION_TOKEN`.
3. In your workflow, set the environment variable `ARTICLES_MEDIUM_ENABLED=true` (or simply rely on the secret – the bot auto‑detects it).
4. The next run will publish articles to both dev.to and Medium.

## 2. Twitter/X Thread Publishing (twitter)

1. Apply for a **Twitter Developer** account at https://developer.twitter.com.
2. Create a Project/App and generate the four credentials:
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_SECRET`
3. Add each as a GitHub secret with the exact names above.
4. (Optional) Set `TWITTER_ENABLED=true` in the workflow environment.
5. The bot will start posting threads after the next successful run.

## 3. Anthropic Claude Backup (llm_anthropic)

1. Sign up at https://console.anthropic.com and obtain a free API key.
2. Add the secret `ANTHROPIC_API_KEY` to the repository.
3. No additional configuration is needed; the bot will automatically fall back to Claude when other providers fail.

## 4. Crypto Trading & Payout (crypto_binance, crypto_payout)

- **Binance API**: Create an API key/secret with trading permissions and add `BINANCE_API_KEY` and `BINANCE_SECRET_KEY`.
- **Withdrawal**: Add `BINANCE_WITHDRAW_ADDRESS` (must be whitelisted in your Binance account) and optionally set `BINANCE_WITHDRAW_NETWORK` if different from the default.

## 5. NFT Minting (nft_ethereum)

1. Generate an Ethereum private key and address.
2. Add `ETH_PRIVATE_KEY` and `ETH_WALLET_ADDRESS` as secrets.
3. Deploy an ERC‑721 contract and set `NFT_CONTRACT_ADDRESS`.
4. (Optional) Add `NFT_STORAGE_TOKEN` for IPFS pinning.

---

After adding the required secrets, push a commit or re‑run the workflow. The bot will automatically detect the new capabilities and start earning.