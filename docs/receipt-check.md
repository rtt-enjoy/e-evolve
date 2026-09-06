# Receipt Check — Independent Footer Verification

## What it does

Every cycle, `receipt_check` fetches the highest-traffic published dev.to posts
from the **unauthenticated public endpoint** and checks whether the USDT tip
footer is actually present in what readers see.

```bash
curl -s "https://dev.to/api/articles/<id>" | grep -c "Support this work"
```

This is not a self-report. It reads the public article body, not the account's
own authenticated view. The two can disagree when the serializer changes, which
is exactly how the 14-cycle outage hid: the authenticated view returned `body_markdown`
while the public endpoint was returning a different field name or empty body.

## What it finds

| Field | Meaning |
|---|---|
| `checked` | Posts observed this cycle |
| `with_footer` | Posts where the tip footer is present in the public body |
| `without_footer` | Posts where it is absent (reader has no way to pay) |
| `unreachable` | Could not fetch the post at all (429, timeout, API change) |
| `missing` | List of posts without the footer, sorted by views descending |
| `last_reason` | `all_verified` = all observed posts carry the footer; `footer_missing` = at least one is missing |
| `agrees_with_backfill` | `true` means the backfill's `remaining` count matches the observation; `false` means the backfill's self-report is wrong |

## When it matters most

The moment the payout footer goes live for the first time, `without_footer`
jumps to 4 or more (the oldest posts were never backfilled). Over the next few
cycles backfill catches up and `without_footer` drops to 0. If it stays non-zero
after backfill reports `remaining: 0`, `agrees_with_backfill` will be `false`
and `receipt_check.last_reason` will be `footer_missing` — the clearest signal
that the receive path is broken for real readers.

## Relationship to backfill

| Module | Does | Never |
|---|---|---|
| `backfill` | Adds the footer to published posts via `PUT /api/articles/{id}` | Reads the public endpoint |
| `receipt_check` | Reads the public endpoint | Writes to dev.to |

They share no serializer and no code path. `receipt_check` exists specifically
to observe what `backfill` cannot see about itself.

## Fields it writes to `status.json`

```json
{
  "receipt_check": {
    "checked": 5,
    "with_footer": 1,
    "without_footer": 4,
    "unreachable": 0,
    "missing": [
      { "id": 4430049, "title": "...", "views": 92, "url": "..." }
    ],
    "last_run": "2026-09-06T06:04:46+00:00",
    "last_reason": "footer_missing",
    "agrees_with_backfill": true
  }
}
```

## Enabling / disabling

`receipt_check` is controlled by `config/strategy.json`:

```json
{
  "receipt_check": {
    "enabled": true,
    "max_per_cycle": 5,
    "history_limit": 50
  }
}
```

`enabled: false` skips the check silently. There is no reason to disable it
once the payout footer is live, because it is the only signal that confirms
readers can actually reach the wallet.