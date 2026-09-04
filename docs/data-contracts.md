# E-Evolve Data Contracts

A reference for what each module reads from and writes to `status.json`,
`docs/status.json`, and the per-module report files. Intended for a new
contributor who has not read every module yet; if a section here disagrees
with the code, the code wins and this file is the bug.

Keys live under `status["..."]` unless stated otherwise. Numeric values
are floats unless the name says `count`/`published`.

## `status["version"]`
Current bot version string, written by the evolution cycle.

## `status["active_features"]` / `status["inactive_features"]`
Lists of feature ids the orchestrator has detected from secrets + config.
Driven by `bot/github_secrets.py`.

## `status["secret_readiness"]`
Per-feature `{active, present[], missing[], present_count, required_count}`.
Same source as `active_features`; the orchestrator reads this to decide
which products to run.

## `status["article_daily"]`
`{date, published}` — `date` is the UTC day the cap applies to, `published`
is the count published on that date. Reset on the calendar day, not on an
elapsed interval.

## `status["article_history"]`
`{source_urls[], source_titles[], titles[], own_urls[], followed_up_ids[]}`.
Each list is bounded by `strategy.json:articles.history_limit` (default 200).

- `source_urls`/`source_titles` — what trending sources have already been
  used, so a fresh take never repeats one.
- `titles` — every published article's normalised title, for near-duplicate
  detection on the title alone.
- `own_urls` — this account's dev.to URLs, written by `devto_stats.fetch_published`.
- `followed_up_ids` — dev.to article ids that have already had a deeper
  follow-up, so the top-performer path cannot mine the same winner twice.

## `status["article_stats"]`
`{count, total_views, avg_views, best_title, best_views, best_url, winning_tags}`.
Refreshed every cycle that touches `articles.run`.

## `status["article_interest"]`
`{archetypes[], best_archetype, worst_archetype, sample_size}`. Each
archetype row is `{archetype, count, avg_engagement, avg_views, best_title}`.
`sample_size < 6` means the report is still raw material, not a signal.

## `status["article_rejects"]`
`{last_reason, last_detail, last_at, counts{}, total}`. `counts` is keyed
by the rejection code from `_REJECTS` in `bot/earning/articles.py`.

## `status["newsletter_daily"]`
`{enabled, date, published_at, published, last_item_count, last_title, last_url}`.

## `status["newsletter_history"]`
`{source_urls[], source_titles[]}`. Separate from `article_history` on
purpose — the same story can be both a digest paragraph and a deeper
article later.

## `status["backfill"]`
`{done_ids[], skipped{}, updated_total, last_run, last_reason, remaining}`.
`done_ids` is the set of dev.to article ids the footer has already been
appended to in this lifetime, so the per-cycle cap does not re-touch them.

## `status["wallet"]`
`{configured, address_masked, network, confirmed_usd, received_total_usd,
last_received_usd, last_received_at, checked_at, stale, error,
balance_high_water_usd}`. `received_*` is the only number this project
treats as real revenue.

## `status["attribution"]`
`{receipts[], receipt_count, total_attributed_usd, last_receipt_at,
by_archetype[], by_tag[], note}`. Written by `bot/earning/attribution.py`
once per real on-chain receipt. Every record carries `confidence:
"correlated"`; TRC-20 has no memo, so this is correlated context, not
per-post proof.

## `status["payout"]` / `status["payout_public"]`
- `payout` — diagnostic snapshot for the owner; address is masked.
- `payout_public` — what the GitHub Pages dashboard publishes. Full address
  lives here on purpose, but only when the footer would also publish it.

## `status["code_tech_earning"]`
`{enabled, last_refresh_at, daily_target_usd, refresh_hours,
opportunities[], requirements[], reference_sources[], remote_service_niches[],
free_ai_focus[], monetization_patterns[], online_ai_brief, focus[],
strategy_playbook[], avoid_patterns[]}`. `online_ai_brief` is the LLM
overlay; everything else is deterministic and survives an LLM outage.

## `status["mrr_ideas"]`
`{enabled, last_refresh_at, refresh_hours, constraints[], summary,
ranked_ideas[], validation_steps[], owner_actions[], viable[], refused[],
llm_used}`. `viable`/`refused` come from the deterministic triage in
`bot/earning/mrr_ideas.py`; `ranked_ideas` comes from one LLM call when
available.

## `status["mrr_ideas_history"]`
`{names[]}` — model names already surfaced, bounded.

## `status["earnings"]`
`{total_usd, this_week_usd, last_cycle_usd, week_started, breakdown{},
confirmed_usd, received_total_usd, last_received_usd, source}`.
`breakdown` is per-product zero-fills (`dev.to`, `code_techs`, `mrr-ideas`,
`dev.to-newsletter`). The on-chain USDT balance is the only number this
object trusts.

## Report files under `docs/`

- `docs/code-tech-opportunities.md` — full ranked leads table plus brief.
- `docs/mrr-ideas.md` — triage + refusal table.
- `docs/earnings-log.md` — append-only per-cycle log of every action.
- `docs/status.json` — public snapshot, sanitised via `bot.status.sanitize_for_git`.

## Public status vs internal status

`status.json` on disk is internal. `docs/status.json` is the sanitised
public copy. They share keys but the public copy drops secrets, raw env
values, and any path the owner has not chosen to expose. New keys should
default to internal; only the dashboard should opt them into public.