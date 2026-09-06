# Receipt Check

This module verifies that published dev.to posts actually carry the USDT tip footer, by reading each post from the **unauthenticated** public endpoint (`GET /api/articles/{id}`) rather than the account's own authenticated view.

## Why it exists

Before this check, the only signal about the receive path was `backfill.remaining`, computed from the same `fetch_published` call that performs the backfill. When that call returned wrong data, the work and the claim about the work were wrong *together*, and agreed with each other. Between cycles #1760 and #1773, `status["backfill"]` read `remaining: 0, last_reason: "nothing_to_do"` while not one of the account's 11 published posts carried a footer -- including the 1,722-view article holding 84% of all lifetime reach.

## How it works

1. Takes the post list (ids and view counts only) from `articles._refresh_stats`.
2. Re-fetches each post's `body_markdown` from the public endpoint -- no API key, no shared serializer.
3. Asserts `payout.has_footer(body)` is true.
4. Compares its finding against `backfill.remaining` and records `agrees_with_backfill`.
5. Logs loudly and reports `without_footer > 0` when any checked post lacks the ask.

## Status fields

- `receipt_check.checked` -- posts observed this cycle
- `receipt_check.with_footer` -- posts confirmed to carry the ask
- `receipt_check.without_footer` -- posts missing the ask
- `receipt_check.unreachable` -- posts that could not be read
- `receipt_check.missing` -- list of posts missing the footer (id, title, views, url)
- `receipt_check.agrees_with_backfill` -- whether the observation matches backfill's claim
- `receipt_check.last_reason` -- `all_verified`, `footer_missing`, `unreachable`, `no_posts`, `disabled`

## Policy

- **Never writes to dev.to.** Repair belongs to `backfill`.
- **Never makes an LLM call.** The comparison is exact.
- **Never raises.** Measurement must not break the cycle.