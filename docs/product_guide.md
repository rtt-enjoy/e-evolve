# Wallet Embedding Guide for Passive Income

This guide shows how to embed your Tron (TRC-20) wallet address across your GitHub repository, product pages, and articles to enable passive USDT/USDC/USDD payments without any platform fees or KYC.

---

## Your Receive Address

**Network:** TRC-20 (Tron)
**Address:** `TFTNsfyomKrnUutRjBTGVULp19ByW29KbY`
**Assets:** USDT, USDC, USDD

> This address is already appended to every article published via the bot (see `bot/earning/payout.py`). The same address should appear everywhere your product is discovered.

---

## 1. GitHub Repository (FUNDING.yml)

Create `.github/FUNDING.yml` in your repository:

```yaml
# .github/FUNDING.yml
github: [your-github-username]
custom: ["https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY"]
```

This adds a "Sponsor" button to your repo that links directly to your Tron address on Tronscan. No GitHub Sponsors enrollment required.

**Verification:** Visit your repo → click "Sponsor" → confirm it opens your Tronscan address page.

---

## 2. README.md

Add a clear support section at the top or bottom of your README:

```markdown
## Support This Work

These tools and articles are researched and published with no paywall, sponsor, or tracking. If one saved you an afternoon, a small tip keeps them coming.

**USDT / USDC / USDD (TRC-20):**
```
TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
```

[![Send USDT on Tron](https://img.shields.io/badge/Send%20USDT-Tron%20(TRC--20)-orange?logo=tron)](tron:TFTNsfyomKrnUutRjBTGVULp19ByW29KbY?amount=5&token=USDT)
```

The `tron:` URI scheme opens the user's wallet app pre-filled with your address.

---

## 3. GitHub Releases

When you publish a product (browser extension, CLI tool, template pack) as a GitHub Release:

1. Include the wallet address in the release notes
2. Add a "Support" section with the same address
3. Link to the Tronscan page for verification

Example release note template:

```markdown
## FocusFlow v1.0.0

A browser extension that automatically blocks distracting websites during focus sessions.

### Download
- [focusflow-v1.0.0.zip](https://github.com/your-repo/releases/download/v1.0.0/focusflow-v1.0.0.zip)

### Support
If this tool helps you, consider a tip:

**USDT/USDC/USDD (TRC-20):** `TFTNsfyomKrnUutRjBTGVULp19ByW29KbY`
[View on Tronscan](https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY)
```

---

## 4. Product Page / Documentation

If you host a product page (GitHub Pages, Netlify, Vercel, etc.):

- Add the wallet address in the footer
- Include a "Buy me a coffee" style button with the `tron:` URI
- Show the Tronscan verification link

Example HTML snippet:

```html
<footer class="support-footer">
  <p>This tool is free. If it saved you time:</p>
  <a href="tron:TFTNsfyomKrnUutRjBTGVULp19ByW29KbY?amount=5&token=USDT" class="btn-crypto">
    Send 5 USDT (Tron)
  </a>
  <p><small>Address: <code>TFTNsfyomKrnUutRjBTGVULp19ByW29KbY</code> | <a href="https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY" target="_blank">Verify on Tronscan</a></small></p>
</footer>
```

---

## 5. CLI Tool --help Output

If your product is a CLI tool, embed the address in `--help` and `--version`:

```python
# In your CLI entry point
EPILOG = """
Support this work:
  USDT/USDC/USDD (TRC-20): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
  Tronscan: https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
"""

parser = argparse.ArgumentParser(..., epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
```

Every time a user runs `--help`, they see the address.

---

## 6. dev.to Articles (Already Automated)

The bot automatically appends this footer to every published article via `bot/earning/payout.py`:

```markdown
---

## Support This Work

These write-ups are researched and published with no paywall, sponsor, or tracking. If one saved you an afternoon, a small tip keeps them coming.

**USDT, USDC or USDD (TRC-20):** `TFTNsfyomKrnUutRjBTGVULp19ByW29KbY`
[Verify on Tronscan](https://tronscan.org/#/address/TFTNsfyomKrnUutRjBTGVULp19ByW29KbY)
```

**Verification:** Run `receipt_check` — it confirms every published article carries this footer.

---

## 7. Getly Storefront (Zero-Cost Channel)

[Getly](https://www.getly.store/sell/crypto) is a digital goods storefront that:
- Costs $0 to list
- Pays out USDT/USDC on Tron directly to YOUR wallet
- No KYC for crypto settlement
- Minimum payout: $15 on Tron

**Setup:**
1. Create free account at getly.store
2. Connect your Tron wallet (`TFTNsfyomKrnUutRjBTGVULp19ByW29KbY`)
3. Upload your product (extension zip, template pack, etc.)
4. Set price (one-time license recommended)
5. Payouts arrive in your wallet automatically on the 1st and 15th

---

## Verification Checklist

- [ ] `.github/FUNDING.yml` exists with custom Tronscan URL
- [ ] README.md contains the wallet address and `tron:` URI
- [ ] GitHub Releases include the address in notes
- [ ] Product page / docs footer has the address
- [ ] CLI `--help` output shows the address
- [ ] dev.to articles carry the footer (automated via bot)
- [ ] Getly storefront connected to the same Tron address
- [ ] `receipt_check` passes (run via bot status command)

---

## Why This Works

| Principle | How It's Satisfied |
|-----------|-------------------|
| **No new secret** | Uses existing `USDT_WALLET_ADDRESS` |
| **No owner action per sale** | Payments go direct to wallet |
| **Within policy** | No outreach, no social posting, no trading |
| **Verifiable on-chain** | Every payment visible on Tronscan |
| **Reuses existing output** | Articles, releases, README already exist |
| **Zero marginal cost** | No per-user server or platform fees |

---

## Next Steps

1. **Commit FUNDING.yml** to your repository
2. **Update README.md** with the support section
3. **Create a GitHub Release** for your first product with the address in notes
4. **Set up Getly** account and list your product
5. **Run `receipt_check`** to verify article coverage
6. **Monitor wallet** via the dashboard (status.json → wallet section)

Every surface that shows your work should show your wallet address. The reader who values your work should never be more than one click away from paying you.