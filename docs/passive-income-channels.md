# Passive Income Channels

This page records the verified channel table from `bot/earning/code_techs.py` so the research is reviewable without reading the full module. Revenue is the on-chain USDT balance only; nothing here is an estimate.

## Receive path

- **Network:** TRC-20 (Tron)
- **Address:** `TFTNsfyomKrnUutRjBTGVULp19ByW29KbY`
- **Asset:** USDT, USDC, or USDD
- **Heading:** Support this work
- **Note:** These write-ups are researched and published with no paywall, sponsor, or tracking. If one saved you an afternoon, a small tip keeps them coming.

## Verified channels

| Channel | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- |
| Getly — sell a digital product, settle USDT on Tron to your own wallet | $0.00 (free to list) | USDT/USDC on Tron (TRC-20) to own wallet, no KYC for crypto settlement | Owner signs up (no ID upload), adds the Tron receive address, and uploads the product once. | After setup, storefront handles delivery and automatic payout once minimum threshold met; no owner action per sale |
| itch.io — free to publish, but a payout needs a tax interview and a TIN | $3.00 one-time identity fee | Fiat via PayPal/Payoneer only; no crypto | Owner creates an account, completes the tax interview with a TIN/SSN, pays the one-time $3 identity fee, and adds fiat payout details. | Publishing is free; payouts are fiat only and require identity verification |
| Chrome Web Store — one-time $5, covers up to 20 extensions | $5.00 one-time | None directly; monetisation via wallet address in description | Owner pays the one-time $5 registration and submits the extension for review. | Once published, users discover organically; wallet address collects payments without owner action |
| Wallet ask on the product page and in every article (already live) | $0.00 (free to list) | USDT/USDC/USDD on Tron (TRC-20) to own wallet | None. Already publishing. | Already running, so it needs no account and no owner action; pays in stablecoin, so the receive path is on-chain and verifiable |

## Refused channels

| Channel | Why refused |
| --- | --- |
| Sellix | Seized and shut down in 2024. Still widely recommended as the crypto storefront, which is exactly why it is written down here as refused. |
| Gumroad (for crypto) | Does not natively accept crypto and pays out USD via Stripe only. Fine as a fiat storefront; it is not a crypto receive path. |
| Buy Me a Coffee / Ko-fi (main platforms) | No native stablecoin field for a supporter's own wallet. |
| Any custodial crypto payment processor | Holds the money before the owner does. The published Tron address is non-custodial and already works. |
| Coinbase Commerce | DEFUNCT. Permanently shut down 2026-03-31 for merchants outside the US/Singapore. |
| CoinPayments | Geo-dead and KYC-mandatory. EU/EEA service discontinued after 2026-07-01 under MiCA. |
| kofi.network | IMPOSTOR RISK -- not affiliated with ko-fi.com despite the name. |
| NOWPayments (as a direct channel) | Marketed as non-custodial, but the default flow routes funds through their wallet and KYC triggers at volume. |
| Gitcoin / Allo | Wound down. Grants Lab and Grants Stack reached end-of-life 2025-05-31. |
| Drips Network | Genuinely non-custodial, but Ethereum ERC-20 only. Cannot reach the Tron address this project publishes. |
| BTCPay Server | The only fully non-custodial, fee-free, no-KYC option -- and it needs a server. This project has none. |
| Gumroad, Substack, Polar, GitHub Sponsors, Ko-fi, Buy Me a Coffee, Payhip, Liberapay, Lemon Squeezy, Paddle, Open Collective | All require identity verification, directly or through Stripe/PayPal onboarding, and none settles crypto to a seller-controlled address. |

## Local playbook

| Lead | Cost | Owner setup | Why passive |
| --- | --- | --- | --- |
| Put the receive address in the GitHub repo itself — FUNDING.yml, README, and releases | $0.00 (free to list) | None beyond committing a file to the repo the owner already controls. | settles to the wallet address this project already publishes; sells the product while nobody is working; the signup is one-time |
| Publish the product as a downloadable file, priced by an honest ask, hosted on GitHub Releases | $0.00 (free to list) | None. Uses the repo the owner already has. | settles to the wallet address this project already publishes; sells the product while nobody is working; the signup is one-time |
| Ask in the artifact, not only beside it — README, --help output, and docs footer | $0.00 (free to list) | None. | settles to the wallet address this project already publishes; sells the product while nobody is working; the signup is one-time |
| Ship the product free, sell the upgrade, ask in the README | not published - do not quote or invent a figure | nothing | sells the product while nobody is working; the signup is one-time |
| One product, listed on every free channel at once | not published - do not quote or invent a figure | open the account | sells the product while nobody is working; the signup is one-time |
| Write the article that the product is the answer to | $0.00 (free to list) | nothing | free tooling or reach to build and market the product with |
| Free-tier stack so the product costs nothing to run | $0.00 (free to list) | nothing | free tooling or reach to build and market the product with |
| Open-source the tool and take sponsorship on the repo | $0.00 (free to list) | nothing | free tooling or reach to build and market the product with |

## Requirements

- Every lead must move a digital product toward earning without the owner in the loop.
- Rank by how little owner action each unit of income needs, not by headline upside.
- Name where the money lands, and prefer stablecoin to the address this project already publishes.
- State every cost and every manual setup step out loud; zero budget is the constraint.
- Never suggest selling the owner's hours: a rate per hour is a job, not passive income.
- Stay inside policy: no social posting, no trading, no minting, no cold outreach.
- Do not count discovery, pipeline, or speculative upside as earnings. On-chain or nothing.