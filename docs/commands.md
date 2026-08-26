# Owner Commands

Two delivery methods — both work the same way:

1. **`command.txt`** — write commands, commit. Next cycle executes and clears them.
2. **GitHub Issue** — create issue with command as title, add label `bot-command`. Bot closes the issue after executing.

Commands are case-insensitive, one per line. Comment lines (starting with `#`) are preserved.

---

## Command Reference

| Command                   | Effect                                                        |
|---------------------------|---------------------------------------------------------------|
| `force articles N`        | Publish N articles now, bypassing the daily cap (max 5)       |
| `force newsletter`        | Publish a newsletter digest now, bypassing the weekly cadence |
| `force trade aggressive`  | Ignored; trading is disabled by policy                        |
| `force mint N`            | Ignored; minting is disabled by policy                        |
| `skip evolution`          | No-op; Phase 3 is already a no-op (Codex owns code changes)   |
| `reset earnings`          | Zero `this_week_usd` counter                                  |
| `post thread`             | Ignored; social posting is disabled by policy                 |
| `improve suggestion TEXT` | No-op; code changes are owned by Codex, not the bot           |
| `status report`           | Dump full `status` dict to workflow log                       |

Both publish commands still respect the content gates. `force newsletter` bypasses
only the *cadence* — if every trending story has already been featured, the digest
publishes nothing rather than repeating itself.

---

## How It Works

`commands.py` reads commands in Phase 2 and stores parsed values in `status['_overrides']`.
This dict is consumed by Phase 4, then stripped before saving to `status.json`.

Overrides are runtime-only — they do not persist to the next cycle.

---

## Example: command.txt

```
# Posted 2026-04-30 — kick off weekly test
force articles 2
force newsletter
status report
```

After the next cycle, executed lines are removed; `#` comment lines stay.
