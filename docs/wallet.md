# Tron USDT Receive Address

This project is paid in stablecoin on the Tron network. The same address is
printed in the footer of every published article, on the product page, and in
`.github/FUNDING.yml`.

## Address

```
TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
```

## Network

TRC-20 (Tron). Send USDT, USDC, or USDD on Tron only.

## What to send

- **USDT (TRC-20)** — preferred
- **USDC (TRC-20)**
- **USDD (TRC-20)**

## Why Tron

- Near-zero transaction fees (~$0.50-1)
- Fast settlement (~3 seconds)
- No KYC for the recipient
- Non-custodial: funds land directly in the wallet

## Verification

The on-chain balance is checked every cycle and reported in `status.json`
under `wallet`. The `receipt_check` module verifies that every published
article carries the footer with this address.