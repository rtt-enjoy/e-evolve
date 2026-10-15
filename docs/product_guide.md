# Wallet Embedding Guide — Passive USDT/USDC Receipts on Tron (TRC-20)

**Receive address:** `TFTNsfyomKrnUutRjBTGVULp19ByW29KbY`
**Network:** TRC-20 (Tron)
**Assets:** USDT, USDC, USDD

---

## Why This Matters

This project publishes daily technical articles to dev.to (34+ posts, 4,675+ views). Every article carries a footer with the wallet address above. **85% of all historical views are on posts published before the footer existed** — backfill is adding it retroactively.

The same address should appear on every surface where a potential payer lands:
- GitHub repository (FUNDING.yml, README, Releases)
- Product pages and documentation
- CLI tools (--help, about command)
- Article footers (already live via `bot/earning/payout.py`)

No platform fees. No KYC. No custodian. The payer sends stablecoin directly to the address; the bot verifies on-chain via `receipt_check`.

---

## 1. GitHub Repository

### FUNDING.yml (Sponsor Button)

Create `.github/FUNDING.yml`:

```yaml
# .github/FUNDING.yml
github: [your-github-username]
custom:
  - "https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"
  - "tron:TFTNsfyomKrnUutRjBTGVULp19ByW29KbY?amount=5&token=USDT"
```

- `custom:` accepts arbitrary URLs — **no GitHub Sponsors enrolment, no Stripe, no W-9**.
- The `tron:` URI scheme opens the user's wallet app pre-filled (if supported).
- Tronscan link lets anyone verify the address and balance publicly.

### README.md

Add a "Support this work" section:

```markdown
## Support this work

These write-ups are researched and published with no paywall, sponsor, or tracking.
If one saved you an afternoon, a small tip keeps them coming.

**USDT / USDC / USDD (TRC-20 / Tron)**

```
TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
```

[View on Tronscan](https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY)
```

### GitHub Releases

Every release description should include:

```markdown
## Download

[focus-flow-v1.0.0.zip](https://github.com/your/repo/releases/download/v1.0.0/focus-flow-v1.0.0.zip)

---

**Like this tool?** It's free to use. If it saves you time, a tip is appreciated:

**USDT/USDC/USDD (TRC-20):** `TFTNsfyomKrnUutRjBTGVULp19ByW29KbY`

[Tronscan](https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY)
```

---

## 2. Product Page / Documentation Site

If you host a product page (GitHub Pages, Netlify, Vercel — all free tiers):

```html
<!-- In <footer> or sticky banner -->
<section class="support">
  <h3>Support this project</h3>
  <p>No paywall, no tracking. Tip if it helped:</p>
  <code id="wallet-address">TFTNsfyomKrnUutRjBTGVULp19ByW29KbY</code>
  <button onclick="navigator.clipboard.writeText(document.getElementById('wallet-address').textContent)">Copy</button>
  <a href="https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY" target="_blank" rel="noopener">Verify on Tronscan</a>
  <small>USDT / USDC / USDD on Tron (TRC-20)</small>
</section>
```

Add a QR code for mobile wallets:

```bash
# Generate once, commit to repo
qrencode -o docs/wallet-qr.png "tron:TFTNsfyomKrnUutRjBTGVULp19ByW29KbY?amount=5&token=USDT"
```

---

## 3. CLI Tools (--help, --version, about)

Every CLI tool this project ships should print the address in `--help`:

```text
$ focus-flow --help
FocusFlow v1.0.0 — Block distractions, keep focus.

Usage: focus-flow [start|stop|status|config]

Options:
  --help       Show this help
  --version    Show version
  --about      Show project info and support address

Support this project (USDT/USDC/USDD on Tron):
  TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
  https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
```

Implementation (Python/argparse example):

```python
import argparse

WALLET = "TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"
TRONSCAN = f"https://tronscan.org/#/address/{WALLET}"

def add_wallet_footer(parser: argparse.ArgumentParser) -> None:
    parser.epilog = f"""Support this project (USDT/USDC/USDD on Tron):
  {WALLET}
  {TRONSCAN}"""
    parser.formatter_class = argparse.RawDescriptionHelpFormatter
```

---

## 4. dev.to Articles (Already Live)

`bot/earning/payout.py` appends this footer to every published article:

```markdown
---

## Support this work

These write-ups are researched and published with no paywall, sponsor, or tracking.
If one saved you an afternoon, a small tip keeps them coming.

**USDT, USDC or USDD (TRC-20 / Tron)**

`TFTNsfyomKrnUutRjBTGVULp19ByW29KbY`

[Verify on Tronscan](https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY)
```

Backfill (`bot/earning/backfill.py`) is adding this to all 34 existing posts.

---

## 5. Getly Storefront (Verified Channel)

[Getly](https://www.getly.store/sell/crypto) — digital goods storefront with native stablecoin payouts:

- **Free to list**, no monthly fee
- **Payouts:** USDT/USDC on Tron (TRC-20) directly to your wallet
- **No KYC** for crypto settlement (verified 2026-09-15)
- **Minimum payout:** $15 on Tron (1st & 15th monthly)
- **Network fee:** ~$0.50-1 per payout (deducted from payout)

**Setup (owner does once by hand):**
1. Create free Getly account
2. Add Tron wallet address `TFTNsfyomKrnUutRjBTGVULp19ByW29KbY`
3. Upload product (ZIP, PDF, license key, etc.)
4. Set price (one-time licence recommended)

---

## 6. Chrome Web Store (Distribution Channel)

- **One-time $5** registration (covers up to 20 extensions)
- **No revenue share** on free extensions
- **Real organic discovery** — users search the store
- **Monetisation:** wallet ask in extension popup / options page, or paid upgrade via Getly

**Setup (owner does once by hand):**
1. Pay $5 at [developer.chrome.com](https://developer.chrome.com/docs/webstore/register)
2. Submit extension for review
3. In extension popup/options, show the wallet address

---

## 7. Verification Checklist

After embedding, run the bot's `receipt_check` to confirm coverage:

```bash
# In repo root
python -m bot.earning.receipt_check
```

Expected output: all published articles show `ok: true` with footer present.

---

## 8. What NOT To Do

| Platform | Why Refused |
|---|---|
| Sellix | Seized 2024, still widely recommended |
| Gumroad / Substack / Polar / Stripe | Require government ID, pay out fiat only |
| Buy Me a Coffee / Ko-fi | No native stablecoin to own wallet |
| Coinbase Commerce | Defunct 2026-03-31 outside US/SG |
| CoinPayments | Geo-dead (EU/EEA), KYC mandatory |
| kofi.network | Impostor — not affiliated with ko-fi.com |
| NOWPayments (direct) | Custodial default flow, KYC at volume |
| Gitcoin / Allo | Wound down 2025-05-31 |
| Drips Network | Ethereum only, cannot reach Tron address |
| BTCPay Server | Needs a server (GitHub Actions is outbound-only) |

---

## 9. Quick Reference

```text
Address:     TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
Network:     TRC-20 (Tron)
Assets:      USDT, USDC, USDD
Tronscan:    https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
URI:         tron:TFTNsfyomKrnUutRjBTGVULp19ByW29KbY?amount=5&token=USDT
QR Code:     docs/wallet-qr.png (generate with qrencode)
```

---

*This guide is maintained by the bot. See `bot/earning/payout.py` for the footer template and `bot/earning/receipt_check.py` for verification logic.*