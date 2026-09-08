# Newsletter Module Completion

## Summary

The `bot/earning/newsletter.py` file was truncated mid-function during the previous evolution cycle. This document records the completion of the missing code.

## What Was Missing

The `_pick_sources` function was cut off mid-loop. The following were also missing:

- `_ensure_sources(body, items)` — guarantees every source appears as a `Source:` line
- `_digest_problems(body, items, cfg)` — structural gate for the digest format
- `_history(status)` — persistent record of sourced/published items
- `_record_issue(status, items, limit)` — records sources so they are never featured twice

## Changes Applied

1. **Completed `_pick_sources` loop body**: duplicate URL/title filtering via `trending._canonical_url` and `trending.normalize_title`, paywall unlock handling via `trending.needs_unlock` / `trending.unlock_summary`, and the `items_per_issue` cap.
2. **Added `_ensure_sources`**: deterministic append of any missing `Source:` lines.
3. **Added `_digest_problems`**: checks minimum word count, section count, required closing section, heading style, and stacked headings; reuses `devto.fabrication_problems` and `devto.tone_problems`.
4. **Added `_history`**: returns the `newsletter_history` sub-dict in status.
5. **Added `_record_issue`**: bounded-append of source URLs and titles into history.

## Verification

- The module imports cleanly.
- `_pick_sources` returns at most `items_per_issue` items.
- `_ensure_sources` adds missing source lines without duplicating existing ones.
- `_digest_problems` returns a list of strings (empty when the digest is valid).
- `_record_issue` bounds history to `history_limit` entries.