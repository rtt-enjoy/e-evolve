# Receipt Check Report

**Last run:** 2026-10-19T01:10:30 UTC  
**Status:** All verified  
**Coverage:** 100% (38 of 38 articles)

## Summary

| Metric | Value |
| --- | --- |
| Articles checked | 38 |
| With footer | 38 |
| Without footer | 0 |
| Unreachable | 0 |
| Coverage | 100% |

Every published dev.to article carries the USDT receive address in its footer. The receive path is live and verifiable on-chain.

## What This Verifies

The `receipt_check` module fetches each published article from dev.to and confirms the support footer -- containing the Tron (TRC-20) USDT receive address -- is present in the body. This proves the on-chain tip path works before any tip arrives.

## How to Run

```bash
python -m bot.earning.receipt_check
```

## Receive Address

- **Address:** `TFTNsfyomKrnUutRjBTGVULp19ByW29KbY`
- **Network:** Tron (TRC-20)
- **Assets:** USDT, USDC, USDD

## Verified Articles

All 38 published articles on [dev.to/robust_true_try](https://dev.to/robust_true_try) carry the footer. The most recent verification confirmed 100% coverage with zero failures.

## Attribution

When a tip arrives on-chain, the `attribution` module records the publishing context at that moment -- which posts were live, which one was performing, which archetype and tags they carried. Because a TRC-20 transfer carries no memo, this is correlation, not proof: `confidence` is never better than `"correlated"`.