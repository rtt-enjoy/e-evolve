# Passive Income Channels

This page records the verified channel table from `bot/earning/code_techs.py`
so the research is reviewable without reading the full module. No code changes,
no secrets, zero cost.

## Verified Channels

| Channel | Cost | Crypto Payout | Owner Setup | Why Passive |
| --- | --- | --- | --- | --- |
| Getly — sell a digital product, settle USDT on Tron to your own wallet | $0 listing | USDT/USDC on Tron (TRC-20) to own wallet, no KYC | Owner signs up (no ID upload), adds the Tron receive address, and uploads the product once. | The storefront delivers the file and processes the payment; the owner receives USDT on-chain with no per-sale action. |
| itch.io — free to publish, but a payout needs a tax interview and a TIN | $3 one-time identity fee | Fiat via PayPal/Payoneer; no crypto | Owner creates an account, completes the tax interview with a TIN/SSN, pays the one-time $3 identity fee, and adds fiat payout details. | After the one-time identity setup, itch.io delivers the file and splits revenue automatically. Note: this channel fails the no-KYC preference because a TIN is required. |
| Chrome Web Store — one-time $5, covers up to 20 extensions | $5 one-time registration | Not a crypto payout channel; the wallet ask for payment lives on the product page linked from the listing | Owner pays the one-time $5 registration and submits the extension for review. | Organic discovery runs on Google's infrastructure; the wallet ask on the linked product page collects payment with no owner action per sale. |
| Wallet ask on the product page and in every article (already live) | $0 | USDT/USDC/USDD on Tron (TRC-20) to own wallet | None. Already publishing. | Already running, so it needs no account and no owner action; pays in stablecoin, so the receive path is on-chain and verifiable. |

## Refused Channels

Written down so a later cycle does not re-derive them, and so a dead
platform cannot climb back onto this page.

- **Sellix:** Seized and shut down in 2024. Still widely recommended as the
  crypto storefront, which is exactly why it is written down here as refused.
- **Gumroad (for crypto):** Does not natively accept crypto and pays out USD via
  Stripe only. Fine as a fiat storefront; it is not a crypto receive path.
- **Buy Me a Coffee / Ko-fi (main platforms):** No native stablecoin field for
  a supporter's own wallet.
- **Any custodial crypto payment processor:** Holds the money before the owner
  does. The published Tron address is non-custodial and already works.
- **Coinbase Commerce:** DEFUNCT. Permanently shut down 2026-03-31 for merchants
  outside the US/Singapore.
- **CoinPayments:** Geo-dead and KYC-mandatory. EU/EEA service discontinued
  after 2026-07-01 under MiCA.
- **kofi.network:** IMPOSTOR RISK -- not affiliated with ko-fi.com.
- **NOWPayments (as a direct channel):** Default flow routes funds through their
  wallet and KYC triggers at volume.
- **Gitcoin / Allo:** Wound down. Grants Lab and Grants Stack reached end-of-life
  2025-05-31.
- **Drips Network:** Ethereum ERC-20 only; cannot reach the Tron address this
  project publishes.
- **BTCPay Server:** Needs a server. This project has none (GitHub Actions is
  outbound-only).
- **Gumroad, Substack, Polar, GitHub Sponsors, Ko-fi, Buy Me a Coffee, Payhip,
  Liberapay, Lemon Squeezy, Paddle, Open Collective:** All require identity
  verification and none settles crypto to a seller-controlled address.

## Local Playbook Leads

| Lead | Cost | Owner Setup | Why Passive |
| --- | --- | --- | --- |
| Put the receive address in the GitHub repo itself — FUNDING.yml, README, and releases | $0 | None beyond committing a file to the repo the owner already controls. | GitHub renders a Sponsor button from .github/FUNDING.yml; the custom: field takes arbitrary URLs with no enrolment. | 
| Publish the product as a downloadable file, priced by an honest ask, hosted on GitHub Releases | $0 | None. Uses the repo the owner already has. | GitHub Releases hosts binaries and archives free, with no storefront, no listing fee, no approval queue and no identity check. | 
| Ask in the artifact, not only beside it — README, --help output, and docs footer | $0 | None. | The address printed in --help, in a docs footer, or in the tool's own about output travels with every copy and every fork. | 
| Ship the product free, sell the upgrade, ask in the README | $0 | None. | A free tool with a paid upgrade earns while nobody is working. | 
| One product, listed on every free channel at once | $0 | One manual signup per channel. | The same digital product listed on each zero-cost storefront multiplies reach without multiplying work. | 
| Write the article that the product is the answer to | $0 | None. | This bot already publishes to dev.to daily; an article about the problem, where the product is the fix and the footer is the ask, is marketing that runs on infrastructure already paid for. | 
| Free-tier stack so the product costs nothing to run | $0 | None. | Client-side work needs no server at all; GitHub Pages hosts a static page and GitHub Actions runs scheduled work, both on the free tier. | 
| Open-source the tool and take sponsorship on the repo | $0 | None. | A public repository is discovery that keeps working after it is published, and the wallet address in the README is a receive path that needs no platform at all. | 

## Verified Address

The Tron (TRC-20) USDT receive address is:

```
TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
```

Network: TRC-20 (Tron)
Asset: USDT, USDC or USDD

This address is already appended to every article this project publishes to
dev.to, and is verified each cycle by `receipt_check`.