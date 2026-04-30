# Owner Commands

Two delivery methods — both work the same way:

1. **`command.txt`** — write commands, commit. Next cycle executes and clears them.
2. **GitHub Issue** — create issue with command as title, add label `bot-command`. Bot closes the issue after executing.

Commands are case-insensitive, one per line. Comment lines (starting with `#`) are preserved.

---

## Command Reference

| Command | Effect |
|---------|--------|
| `force articles N` | Post N articles this cycle (overrides `per_cycle` config) |
| `force trade aggressive` | Raise trade risk to 5% for this cycle |
| `force mint N` | Mint N NFTs this cycle |
| `skip evolution` | Skip Phase 3 (LLM evolution) this cycle |
| `reset earnings` | Zero `this_week_usd` counter |
| `post thread` | Force a Twitter thread even if not otherwise scheduled |
| `status report` | Dump full `status` dict to workflow log |

---

## How It Works

`commands.py` reads commands before Phase 3 and stores parsed values in `status['_overrides']`.  
This dict is consumed by Phases 3 and 4, then stripped before saving to `status.json`.

Overrides are runtime-only — they do not persist to the next cycle.

---

## Example: command.txt

```
# Posted 2026-04-30 — kick off weekly test
force articles 2
post thread
status report
```

After the next cycle, executed lines are removed; `#` comment lines stay.
