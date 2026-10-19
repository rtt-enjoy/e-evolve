# Code Evolution

Phase 3 lets the LLM propose code changes. It is **enabled and human-gated**:
every proposal lands on an `evolve/<version>-<utc>` review branch and reaches
`main` only when a human merges it. The sandbox rules (path allowlist,
protected files, 3-change cap, syntax + import check, review branch) are
described in `CLAUDE.md` under *Safety Boundaries*.

This page covers what the engine is **asked**, because that is what decides
whether a proposal is worth reviewing.

## Why the prompt was rebuilt (2026-10-19)

By cycle #2003 the engine had made 65 proposals in three weeks (47 still open
as `evolve/*` branches, the rest already pruned at 14 days), and none had been
merged. Read together, they failed in four repeating ways:

| Failure | Examples | Cause |
| --- | --- | --- |
| Rebuilt what exists | "add the missing doctrine" x4 (deleting up to 1,191 lines of it), `wallet_verification.py`, `payout_verify.py`, `automated_backfill.py` | The snapshot never included `docs/`, and nothing listed the files that exist |
| Truncated large files | `code_techs.py` -2,069 lines, `payout.py` -416 | The schema demanded the complete file, even for a 1,800-line module |
| Refused directions | GH_TOKEN, "enable Cerebras" x5, `FUNDING.yml` under `.github/`, louder footer CTA, relaxed title gates | The prompt listed inactive secrets as things to activate, and asked for `estimated_weekly_usd` |
| Repeats | four "health diagnostic" modules | No memory of earlier proposals |

The old prompt was a ~97 KB raw `status.json` dump plus the codebase. The
fields the doctrine says to read were buried inside it, next to 37 KB of
lead queues no code change acts on.

## What the engine sees now

`bot/evolution.build_prompt()` assembles, in order:

1. **Owner direction**, when set. `evolution.direction` in
   `config/strategy.json` is a standing direction. The `improve suggestion TEXT`
   command applies for one cycle. Either one outranks the computed brief.
2. **Situation brief.** `checklist_step()` works the doctrine checklist
   deterministically and names the first step that is not clean, with the
   evidence: receive path (`payout.live`, `receipt_check`), then money
   (`wallet`), then reach (`article_interest` with `count` per row,
   `preferred_archetypes()`, `article_rejects.counts` ranked). An unobserved
   cycle (`coverage_complete: None`) does not bind step 1 (Principle 3k).
3. **Operations**: which engine served, errors, the last evolution error, and
   backfill 429s.
4. **Prompt ledger and focus** (`prompt_ledger()`), described below.
5. **Doctrine extract**: every principle heading, plus the checklist and the
   channel table quoted verbatim from `docs/passive-income-doctrine.md`. The
   prompt never restates them, so it cannot drift from the file.
6. **Status digest**: small fields verbatim, large ones by name and size.
   Secret-readiness fields are left out entirely. They only ever produced
   "add a secret" proposals, and a missing secret is an owner decision.
7. **Prior proposals**: the open `evolve/*` branches, read from git refs and
   deduplicated with a repeat count and the files each one touched.
8. **File inventory**: every editable file with its line count, with protected
   files marked.
9. **Codebase**, then the task restated last. The prompt files
   (`articles.py`, `devto.py`, `newsletter.py`) lead the snapshot.

The system prompt carries the known dead ends taken from those 65 proposals.
They are duplicates of existing modules, modules nothing calls (`main.py` is
protected, so a new product is never run), new secrets, `.github/`, loosening
quality gates, tuning the footer before receipts exist, 429 retry loops,
revenue estimates, and anything already proposed.

## Prompt work (owner directive, 2026-10-19)

Every evolution attends to the prompts that write what readers see, and
upgrades them one step at a time, toward more passive income. The prompts are
the main lever on reach. Each draft a gate refuses is one post, and one tip ask,
that never ships. The title and the angle decide how many readers each post
gets.

`_PROMPT_LEDGER` in `bot/evolution.py` names each prompt, its file and symbol,
and the `article_rejects` codes that grade it: article draft (`_SYSTEM` plus the
user prompt in `_generate_article()`), title rewrite (`_revise_title()`),
format revision (`_revise_format()`), follow-up, audience guidance, the shared
`devto.VOICE`, and the newsletter digest. `prompt_ledger()` renders it with:

- **Drafts lost to a prompt**: `weak_title`, `fabricated`, `too_similar` and
  `revision_fabricated`, counted over the last 14 days.
- **Drafts lost to the engine**: `llm_error`, `empty_draft`, `no_llm`. No text
  came back, so no prompt edit moves them, and they are listed apart so the
  engine does not "fix" a prompt for an outage.
- **Prompt focus**: the prompt code with the most losses, the prompts that
  produce it, and the gate's own findings behind it (for example
  `'too long (78 chars)' x4`). With no prompt losses, the focus is the
  outcome: the draft angle and `_audience_guidance()`, steered by
  `article_interest`.

**Why a dated window.** `article_rejects.counts` is a lifetime tally, so a
merged prompt fix never shows in it, and the focus would point at the same
prompt forever. `articles._record_reject` now also keeps
`article_rejects.recent`, the last 50 rejects with `at` and the gate's
`detail`. A fix merged inside the 14-day window lowers its code, and the focus
moves on to the next prompt. That is what makes the work gradual. On a
snapshot without `recent`, the ledger falls back to the lifetime counts and
says so.

When the binding step is reach (step 4), the task line makes the prompt focus
the default change. When step 1 or 2 binds, prompt work waits. The ledger is
left out of compact (Groq) prompts, whose 4 KB snapshot holds no prompt text
to edit.

The system prompt's rules for a prompt change:

- One prompt per cycle, a few-line edit. Never rewrite a whole prompt.
- Quote the focus count and gate findings as evidence, and name the count that
  should fall in `verify`.
- Replace a rule that is not working instead of stacking a new one, so the
  prompts do not grow every cycle.
- Change the instruction, never the gate, and never soften the rules against
  invented figures, bugs, endpoints or URLs.
- Voice rules live once, in `devto.VOICE`.
- An article never asks for money or mentions tips, the wallet, the account or
  its statistics. The footer is deterministic and attached after the gates.

## What a proposal must contain

```json
{
  "version": "X.Y.Z", "summary": "...",
  "direction": "checklist step / principle served",
  "evidence": ["status field = value"],
  "money_path": "where money enters, or reach-only, or none (maintenance)",
  "verify": "test added, or status field that should move",
  "changes": [
    {"file": "bot/earning/x.py", "reason": "...",
     "edits": [{"old": "exact text, occurs once", "new": "replacement"}]},
    {"file": "bot/earning/new.py", "reason": "...", "content": "complete new file"}
  ],
  "suggestions": [{"title": "...", "owner_action": "...", "secret_needed": null, "how_to": []}]
}
```

- **Existing files change by `edits`.** Every `old` must occur exactly once,
  or the whole change is skipped, all or nothing.
- **A full `content` rewrite that keeps less than 60% of an existing file of
  4 KB or more is refused** (`_SHRINK_FLOOR`, `_SHRINK_MIN_BYTES`).
- `direction`, `evidence`, `money_path` and `verify` are persisted in
  `status["last_evolution"]` and written into the review branch's commit body,
  so a reviewer can judge the diff from `git log` alone.
- `estimated_weekly_usd` is gone from the schema (doctrine Principle 4).
- "No change" is a valid answer and is preferred to a speculative one.

## Steering the engine

- Standing: set `evolution.direction` in `config/strategy.json`, for example
  `"cut the llm_error article rejects"`.
- One cycle: `improve suggestion TEXT` in `command.txt` or a `bot-command`
  issue.
- To change the rules themselves, edit `bot/evolution.py`. It is protected, so
  the engine cannot rewrite its own brief.
