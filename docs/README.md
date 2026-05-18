# E‑Evolve Bot Documentation

## Overview
E‑Evolve is an autonomous GitHub Actions bot that continuously improves itself, publishes technical content, trades crypto, mints NFTs, and pursues low‑effort maintenance gigs.

## Quick Start
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/e-evolve.git && cd e-evolve
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure secrets** – add the required API keys as GitHub repository secrets (see the *Suggestions* section for a full list).
4. **Enable features** – edit `config/strategy.json` or use the `force` commands to toggle modules.
5. **Run locally** (optional) to verify:
   ```bash
   python -m bot.main
   ```

## Features
- **Article publishing** – dev.to (always) and Medium (optional).
- **Twitter/X threads** – generate and post developer‑focused threads.
- **Crypto trading** – spot trading on Binance with risk limits.
- **NFT minting** – optional IPFS‑pinned NFTs on Ethereum.
- **Code‑tech earnings** – discover and auto‑pursue small open‑source maintenance gigs.
- **Auto‑payout** – withdraw USDT profits from Binance.

## Adding New Secrets
For any new feature, create a secret in the repository settings:
1. Go to *Settings → Secrets → Actions*.
2. Click **New repository secret**.
3. Name it exactly as listed in the suggestion (e.g., `MEDIUM_INTEGRATION_TOKEN`).
4. Paste the value and save.

## Development
- Run `pytest` to execute the bundled unit tests.
- The bot logs detailed information to `earnings-log.md` and publishes a public dashboard under `docs/`.

## License
MIT © 2026 E‑Evolve contributors