# Product Wallet Embedding Guide

## 1. Locate the Wallet Address

The address to use is:

```
TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
```

## 2. Embed in README

Add a section to your README.md (or at the bottom) with a clear call‑to‑action:

```markdown
## Support this project

If this tool saves you time, you can show your appreciation by sending a small USDT payment to the following address:

**TFTNsfyomKrnUutRjBTGVULp19ByW29KbY** (TRC‑20)

*No account, no KYC, no platform fees – the money goes straight to the developer’s own wallet.*
```

## 3. Embed in Product Pages

Place the address in a prominent location on your product page:

- In the hero section, next to the product description.
- In the "How to pay" subsection, with a short note:

```markdown
### Payment

Send USDT (TRC‑20) to **TFTNsfyomKrnUutRjBTGVULp19ByW29KbY**.
The transaction is on‑chain and verifiable; no intermediary holds the funds.
```

## 4. Update FUNDING.yml (GitHub Sponsor button)

If you use a FUNDING.yml file to enable GitHub Sponsors, add a custom URL field:

```yaml
# .github/FUNDING.yml
name: "Support with USDT"
url: "https://tftn.example.com/donate?address=TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"
```

The `custom:` field accepts any URL, so you can point directly to a simple web page that displays the address.

## 5. Verify the Setup

Run the receipt check to confirm the address is recognized:

```bash
python -c "import bot.earning.receipt_check as rc; rc.check_receipts()"
```

If the address appears in the verified list, the embedding is successful.

## 6. Optional: Add to Release Notes

When you create a new GitHub Release, include the address in the release notes:

```
## Support the project

You can now send USDT (TRC‑20) directly to **TFTNsfyomKrnUutRjBTGVULp19ByW29KbY**.
```

By following these steps, you embed the wallet address where users see it most often, enabling passive income without extra cost or platform dependency.