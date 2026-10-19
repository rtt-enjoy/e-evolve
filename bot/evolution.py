"""
Evolution — Phase 3
Reads the codebase, asks the LLM for improvements, applies them safely.

Hard safety rules (cannot be overridden by LLM output):
  • Only writes files under: bot/, docs/, config/, requirements.txt, version.txt
  • Never touches: .github/, .git/
  • No path traversal (.. rejected)
  • Python files are syntax-checked before writing
  • Existing files change by exact search/replace edits; a full rewrite that
    drops 40%+ of a large file is refused
  • Max 3 file changes per cycle
  • Original files are backed up before overwriting

Post-apply verification (Phase 3.5):
  • Each changed .py file is import-checked in a subprocess
  • On failure: LLM asked to fix (up to MAX_FIX_RETRIES attempts)
  • If still failing: backup restored, file removed from applied list
"""
from __future__ import annotations

import ast
import json
import logging
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# Safety constants
ALLOWED_PREFIXES  = ("bot/", "docs/", "config/", "requirements.txt", "version.txt")
FORBIDDEN_PREFIXES = (".github/", ".git/")
# Orchestrator files the LLM must never overwrite — too risky to allow auto-edit
PROTECTED_FILES = {
    "bot/main.py", "bot/commands.py", "bot/evolution.py",
    "bot/status.py", "bot/llm.py", "bot/git_utils.py",
}
MAX_CHANGES       = 3
MAX_FIX_RETRIES   = 2
# Output budget for one evolution plan. The schema demands COMPLETE file
# contents for up to MAX_CHANGES files; three ~500-line modules plus suggestions
# do not fit in 6k tokens, and the model gets cut off mid-string -- which reads
# as "invalid JSON" but is really "not enough room to finish". Every model in
# the free upgrade chain accepts 32k output.
_MAX_PLAN_TOKENS = 32_000
# A repair returns one rewritten file, so it needs a full file's worth too.
_MAX_FIX_TOKENS  = 16_000
# Per-provider codebase snapshot limits.
# Groq free tier: 12k TPM total — status JSON ~1k, system prompt ~0.6k, response 6k → 4k left for codebase.
# Groq is a fallback only; _MAX_PLAN_TOKENS is sized for Atria and the openrouter
# upgrade chain, so a groq cycle stays capped by that 12k TPM ceiling.
# Gemini/Anthropic: large context, no TPM issue.
# Atria (main engine): Atria-Dawn holds ~256K context and ~65K output
# (third-party listings, 2026-10), so the same 200k-byte snapshot and 32k plan fit.
# OpenRouter: the free upgrade chain leads with 1M-context models and the
# smallest entry still holds 256K, so 30k starved the model -- one module filled
# the whole budget and the other 19 files were skipped, leaving it unable to see
# what it was changing. 200k bytes is ~50k tokens: the whole editable surface,
# well inside every model in the chain.
_MAX_READ_BYTES = {
    "groq":       4_000,
    "anthropic":  60_000,
    "claude-cli": 60_000,
    "gemini":     80_000,
    "openrouter": 200_000,
    "atria":      200_000,
}

# The doctrine is the standing brief for what "evolve" means here, and the
# codebase snapshot never included docs/ -- so the engine evolved blind to it,
# and four separate proposals "added the missing doctrine" by overwriting the
# 1,209-line file with a stub. These sections are quoted verbatim from the file
# on every cycle rather than restated here, so the prompt cannot drift from it.
_DOCTRINE_PATH = "docs/passive-income-doctrine.md"
_DOCTRINE_SECTIONS = (
    "The standing checklist for the next evolution",
    "Candidate channels, scored",
)
# Open evolve/* branches are unmerged proposals. Showing them stops the engine
# re-proposing the same idea hourly: on 2026-10-19 the 47 open branches held
# the "health diagnostic" module four times and "add the doctrine" four times.
_MAX_PRIOR_PROPOSALS = 30
# A status sub-tree larger than this is summarised by name and size, not
# dumped: code_tech_earning alone was 37 KB of the old 97 KB status dump.
_STATUS_FIELD_MAX_BYTES = 1_500
# Fields that only ever led the engine to "add a secret": the old prompt listed
# "Inactive (need secrets): llm_anthropic, llm_cerebras" and five proposals
# then tried to enable Cerebras. A missing secret is an owner decision, never
# a code change, so these are left out of the digest entirely.
_STATUS_BAIT = frozenset({
    "inactive_features", "secret_readiness", "configured_github_secrets",
    "last_earning",
})
# A full-file rewrite that keeps less than this share of an existing file is
# refused. Observed: payout.py -416 lines, code_techs.py -2,069 lines, and the
# doctrine replaced by a 56-line stub -- all from "COMPLETE file" rewrites of
# files too large to reproduce inside one response.
_SHRINK_FLOOR = 0.6
_SHRINK_MIN_BYTES = 4_000

# Every prompt that writes what readers see: (name, file, where, reject codes
# that grade it). A reject is a draft the prompt produced and a gate refused,
# so these codes are the prompt's measured failure rate. Owner directive
# 2026-10-19: every evolution attends to these prompts and upgrades them a
# step at a time, toward more passive income.
_PROMPT_LEDGER = (
    ("article draft", "bot/earning/articles.py",
     "_SYSTEM (TITLE, CONTENT RULES, SOURCE HANDLING) + the user prompt in "
     "_generate_article()",
     ("weak_title", "fabricated", "too_similar")),
    ("title rewrite", "bot/earning/articles.py", "_revise_title()", ("weak_title",)),
    ("format revision", "bot/earning/articles.py", "_revise_format()",
     ("revision_fabricated",)),
    ("follow-up", "bot/earning/articles.py",
     "_FOLLOWUP_EXTRA + the user prompt in _generate_followup()", ()),
    ("audience guidance", "bot/earning/articles.py",
     "_audience_guidance() + _ARCHETYPE_ANGLES, steered by article_interest", ()),
    ("house voice", "bot/earning/devto.py", "VOICE, shared by every writing prompt", ()),
    ("newsletter digest", "bot/earning/newsletter.py",
     "_SYSTEM + the user prompt in run()", ()),
)
_PROMPT_FILES = frozenset(entry[1] for entry in _PROMPT_LEDGER)
# No text came back, so no prompt edit moves these. Naming them stops the
# engine "fixing" a prompt for an engine outage.
_ENGINE_REJECTS = ("llm_error", "empty_draft", "no_llm")
# Matches the review-branch retention: a fix merged inside it shows up here.
_PROMPT_WINDOW_DAYS = 14

_SYSTEM = """\
You are the evolution engine of E-Evolve: an hourly GitHub Actions bot that
publishes developer articles to dev.to with a USDT tip address in every post,
and earns only what readers send to that address. Real revenue is the
on-chain balance. Nothing else counts as money.

Your output is a code proposal on a REVIEW BRANCH. A human reads the diff and
decides whether to merge it. Dozens of earlier proposals were never merged,
mostly because they rebuilt something that already exists, rewrote a large
file and lost code, or went where the project has already decided not to go.
One small, evidenced, verifiable change is worth more than three speculative
ones. Proposing no change is a correct answer when nothing clears the bar.

How to choose the change:
1. Read the SITUATION BRIEF. It is computed from status.json and names the
   doctrine checklist step that binds right now. Serve that step, unless the
   OWNER DIRECTION says otherwise.
2. Ground it in evidence: quote the status fields and values that show the
   problem. No evidence, no change.
3. Say where money enters because of it ("money_path"). If it does not touch
   the receive path, say "reach-only". That is allowed, but say it.
4. Say how the reviewer confirms it worked ("verify"): a test you added to
   bot/tests.py, or a status field that should move next cycle.
5. Find the code that causes the problem in the CODEBASE and change that code.
   A new file is rarely the answer to a problem in an existing one.

Prompts are the main lever. The PROMPT LEDGER lists every prompt that writes
what readers see. Each draft a gate refuses is one post, and one tip ask, that
never ships; the title and the angle decide how many readers each post gets.
Upgrade prompts gradually, one step per cycle:
- One prompt, a few-line edit: sharpen, replace or reorder one rule, or add
  one concrete example. Never rewrite a whole prompt.
- Aim at the PROMPT FOCUS. Quote its reject count and gate findings as
  "evidence"; in "verify", name the count that should fall in the window.
- Replace a rule that is not working instead of stacking a new one beside it.
  A prompt that grows every cycle buries the rules that matter.
- Change the instruction, never the gate. Never soften the rules against
  invented figures, bugs, endpoints or URLs to get a draft through.
- Voice rules live once, in devto.VOICE, shared by every product.
- An article never asks for money and never mentions tips, the wallet, the
  account or its statistics. The footer is attached after the gates on purpose.

Known dead ends. Each was proposed repeatedly and never merged:
- A module that duplicates one in the FILE INVENTORY. Address validation is
  bot/earning/payout.py; retrofitting the footer onto old posts is backfill.py;
  reading posts back to verify the footer is receipt_check.py; the doctrine is
  docs/passive-income-doctrine.md and already exists. Check the inventory
  before creating any file.
- A new module that nothing calls. Only bot/main.py calls product run()
  functions and you cannot edit it, so a new bot/earning/*.py is dead code
  unless an existing editable module imports and calls it. Health, diagnostic
  and summary scripts fail this; status.json and the dashboard already report.
- A new secret, token or account (GH_TOKEN, GITHUB_TOKEN, more LLM keys,
  storefront signups). "Needs no new secret" is rank 1 of the channel table.
- Anything under .github/ (FUNDING.yml, workflows). The sandbox drops it.
- Loosening a quality gate (title, fabrication, tone, min_words, follow-up
  thresholds) to publish more. The gates exist because loose ones published
  junk. Fix the draft, or the prompt that produced it, not the gate.
- Rewording or enlarging the tip footer. Doctrine Principle 5: do not tune the
  ask until receipts exist.
- Retry/backoff loops for HTTP 429. dev.to and Reddit throttle the IP; backfill
  and receipt_check stop at the first failure on purpose, and the next hourly
  cycle is the retry.
- Any revenue estimate. estimated_usd stays 0.0.
- Anything already in PRIOR PROPOSALS. Those branches are still open.

Hard rules, enforced in code (breaking one only wastes the cycle):
- Write only under bot/, docs/, config/, requirements.txt, version.txt.
- Never write bot/main.py, bot/commands.py, bot/evolution.py, bot/status.py,
  bot/llm.py or bot/git_utils.py.
- At most 3 changes. Python must parse and import.
- To change an EXISTING file, use "edits": exact search/replace pairs. Each
  "old" must occur exactly once in the current file, copied character for
  character from the CODEBASE. Use "content" (the complete file) only for a
  new file. A rewrite that drops 40% or more of an existing file is refused.
- Social posting, trading, minting, payouts, cold outreach and commenting on
  external issues stay blocked.

Respond with ONLY one JSON object, keys in this order:
{
  "version": "X.Y.Z (patch for a fix, minor for a feature)",
  "summary": "one sentence: what changes and why",
  "direction": "the checklist step or doctrine principle this serves",
  "evidence": ["status field = value that shows the problem"],
  "money_path": "where money enters because of this, or reach-only, or none (maintenance)",
  "verify": "how the reviewer confirms it worked",
  "changes": [
    {"file": "bot/earning/x.py", "reason": "why, specific enough to review",
     "edits": [{"old": "exact existing text", "new": "replacement"}]},
    {"file": "bot/earning/new_file.py", "reason": "why", "content": "COMPLETE new file"}
  ],
  "suggestions": [
    {"title": "short title", "description": "what it unlocks",
     "owner_action": "the one step only the owner can take",
     "secret_needed": null, "how_to": ["Step 1: ...", "Step 2: ..."]}
  ]
}
"suggestions" are 0-3 actions only the owner can take: none the doctrine
already refuses, never with a dollar estimate. An empty list is fine.
If no change clears the bar, return "changes": [] and say why in "summary"."""


def enabled(cfg: dict[str, Any] | None = None) -> bool:
    """
    Evolution runs only when explicitly switched on in config/strategy.json.

    Default is off: an LLM that writes to this repo on an hourly cron is an
    owner decision, so absence of config means disabled, never enabled.
    """
    cfg = cfg if cfg is not None else _load_config()
    return bool(cfg.get("enabled", False))


def _load_config() -> dict[str, Any]:
    try:
        raw = json.loads(Path("config/strategy.json").read_text(encoding="utf-8"))
        cfg = raw.get("evolution", {})
        return cfg if isinstance(cfg, dict) else {}
    except Exception:
        return {}


def _branch_name(version: str, prefix: str) -> str:
    """Unique, git-legal branch name for one evolution batch."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    # git rejects "..", a leading/trailing ".", and a trailing ".lock"; collapse
    # dot runs so a hostile or malformed version cannot produce an illegal ref.
    safe = re.sub(r"[^0-9A-Za-z._-]", "-", str(version))
    safe = re.sub(r"\.{2,}", ".", safe).strip(".-") or "unversioned"
    return f"{prefix.strip('/') or 'evolve'}/{safe}-{stamp}"


def run(llm: Any, status: dict[str, Any]) -> dict[str, Any]:
    """
    Run evolution. Returns:
      { version_bumped_to, summary, changes_applied, suggestions,
        error, branch, proposed_version }

    Changes are committed to a review branch, never to the working branch.
    """
    from bot.llm import ROLE_PROVIDER
    upgrade_provider = ROLE_PROVIDER.get("upgrade", ROLE_PROVIDER.get("think", "gemini"))
    # Use upgrade-role provider capacity if that key is available, else fallback to default
    key_attr = f"_{upgrade_provider}_key" if upgrade_provider != "claude-cli" else None
    if key_attr and getattr(llm, key_attr, ""):
        evo_provider = upgrade_provider
    else:
        evo_provider = getattr(llm, "provider", "groq")
    max_bytes = _MAX_READ_BYTES.get(evo_provider, _MAX_READ_BYTES["groq"])
    log.info("Evolution provider=%s (upgrade role), max_bytes=%d", evo_provider, max_bytes)
    compact = evo_provider == "groq"
    codebase = _read_codebase(max_bytes, include_config=not compact)
    prompt = build_prompt(status, codebase, _load_config(), compact=compact)

    try:
        plan = llm.complete_json_for_role("upgrade", prompt, system=_SYSTEM, max_tokens=_MAX_PLAN_TOKENS)
    except Exception as exc:
        log.error("Evolution LLM call failed: %s", exc)
        return _error_result(str(exc), status.get("version", "1.0.0"))

    applied  = _apply_changes(plan.get("changes", []), _load_config().get("max_changes"))
    applied  = _verify_and_fix(applied, llm, status)
    version  = _resolve_version(plan.get("version"), status.get("version", "1.0.0"))

    summary = plan.get("summary", "No summary provided")
    branch = None
    branch_error = None

    if applied:
        # version.txt belongs in the reviewed diff, so write it before the branch
        # commit; commit_to_branch reverts it on the working branch afterwards.
        Path("version.txt").write_text(version + "\n", encoding="utf-8")

        import bot.git_utils as _git
        cfg = _load_config()
        branch = _branch_name(version, str(cfg.get("branch_prefix", "evolve")))
        paths = [c["file"] for c in applied] + ["version.txt"]
        result = _git.commit_to_branch(
            _commit_message(version, summary, plan), paths, branch,
        )
        if not result["success"]:
            branch_error = f"branch commit failed: {result['error']}"
            log.error(branch_error)
            branch = None
        elif not result["committed"]:
            branch = None
        else:
            log.info("Evolution parked on %s for review — working branch untouched", branch)

    # The working branch keeps its committed version. The bump ships with the
    # review branch and only takes effect once the owner merges it.
    version = status.get("version", "1.0.0")

    return {
        "version_bumped_to": version,
        "summary":           summary,
        # Strip runtime-only bookkeeping (_backup) so it never reaches status.json.
        "changes_applied":   [
            {k: v for k, v in ch.items() if not k.startswith("_")} for ch in applied
        ],
        "suggestions":       plan.get("suggestions", []),
        # The reasoning a reviewer needs, persisted beside the diff it explains.
        **{k: plan[k] for k in _RATIONALE_KEYS if plan.get(k)},
        "error":             branch_error,
        "branch":            branch,
        "proposed_version":  _resolve_version(plan.get("version"), version),
    }


# ── Prompt composition ───────────────────────────────────────────────────────

_RATIONALE_KEYS = ("direction", "evidence", "money_path", "verify")


def build_prompt(status: dict[str, Any], codebase: str,
                 cfg: dict[str, Any] | None = None, compact: bool = False) -> str:
    """
    The evolution request: what binds now, why, what exists, what was tried.

    The codebase goes last and the task is restated after it, so the closing
    instruction is not 200 KB away from the answer. The prompt carries no raw
    status dump: that was ~97 KB, dominated by queues no change acts on,
    while the few fields the doctrine says to read were buried inside it.
    """
    cfg = cfg if cfg is not None else _load_config()
    step, evidence = checklist_step(status)
    parts = []

    direction = str(cfg.get("direction") or "").strip()
    improve_target = (status.get("_overrides") or {}).get("improve_suggestion")
    if direction or improve_target:
        owner = ["OWNER DIRECTION (outranks the binding step below):"]
        if direction:
            owner.append(f"- Standing direction (config evolution.direction): {direction}")
        if improve_target:
            owner.append(f"- This cycle only: improve the suggestion '{improve_target}' — "
                         "make it actionable or automated inside current policy.")
        parts.append("\n".join(owner))

    parts.append(
        "SITUATION BRIEF (computed from status.json this cycle):\n"
        f"Binding step: {step}\n" + "\n".join(f"- {line}" for line in evidence)
    )
    ops = _operations_lines(status)
    if ops:
        parts.append("OPERATIONS:\n" + "\n".join(f"- {line}" for line in ops))
    if not compact:
        # Compact snapshots hold no prompt text, so an edit there cannot match.
        parts.append(prompt_ledger(status))
        parts.append(_doctrine_extract())
        parts.append("STATUS FIELDS (large sub-trees summarised by size):\n"
                     + _status_digest(status))
    prior = prior_proposals(limit=10 if compact else _MAX_PRIOR_PROPOSALS)
    if prior:
        parts.append(prior)
    parts.append(_file_inventory())
    parts.append(f"CODEBASE:\n{codebase}")
    if step.startswith("4") and not compact:
        task = ("TASK: the binding step is reach, and the PROMPT FOCUS is the default "
                "way to move it. Propose one gradual edit to the prompt it names, "
                "unless the evidence above points more strongly elsewhere, or return "
                "no change and say why.")
    else:
        task = (f"TASK: the binding step is \"{step}\". Propose the smallest change "
                "that moves it, grounded in the evidence above, or return no change "
                "and say why. Prompt work waits until this step is clean.")
    parts.append(task + " Follow the system rules and the dead-end list. JSON only.")
    return "\n\n".join(parts)


def prompt_ledger(status: dict[str, Any], now: datetime | None = None) -> str:
    """
    Every reader-facing prompt, what grades it, and the one to upgrade next.

    Graded on dated rejects inside _PROMPT_WINDOW_DAYS so a merged prompt fix
    moves the focus on to the next prompt. The lifetime counts would point at
    the same prompt forever, which makes gradual work impossible.
    """
    rejects = status.get("article_rejects") or {}
    recent = rejects.get("recent")
    details: dict[str, Counter] = {}
    if isinstance(recent, list):
        now = now or datetime.now(timezone.utc)
        cutoff = now - timedelta(days=_PROMPT_WINDOW_DAYS)
        counts: Counter = Counter()
        for r in recent:
            if not isinstance(r, dict):
                continue
            try:
                at = datetime.fromisoformat(str(r.get("at")))
            except ValueError:
                continue
            if at.tzinfo is None:
                at = at.replace(tzinfo=timezone.utc)
            if at < cutoff:
                continue
            code = str(r.get("code"))
            counts[code] += 1
            if r.get("detail"):
                details.setdefault(code, Counter())[str(r["detail"])] += 1
        basis = f"last {_PROMPT_WINDOW_DAYS} days"
    else:
        counts = Counter({str(k): int(v) for k, v in (rejects.get("counts") or {}).items()})
        basis = "lifetime tally; no dated window recorded yet, so an old fix still counts"

    lines = ["PROMPT LEDGER (the prompts that write what readers see):"]
    for name, path, where, codes in _PROMPT_LEDGER:
        graded = f"graded by {', '.join(codes)}" if codes else "no gate tally"
        lines.append(f"- {name}: {path} {where}; {graded}")

    prompt_codes = [c for entry in _PROMPT_LEDGER for c in entry[3]]
    lost = sorted({c for c in prompt_codes if counts.get(c)},
                  key=lambda c: (-counts[c], prompt_codes.index(c)))
    engine = [c for c in _ENGINE_REJECTS if counts.get(c)]
    if lost:
        lines.append(f"Drafts lost to a prompt ({basis}): "
                     + ", ".join(f"{c}={counts[c]}" for c in lost))
    if engine:
        lines.append(f"Drafts lost to the engine, not fixable by a prompt edit ({basis}): "
                     + ", ".join(f"{c}={counts[c]}" for c in engine))

    if not lost:
        lines.append(f"PROMPT FOCUS: no prompt lost a draft ({basis}). Upgrade on outcome: "
                     "the article draft angle and _audience_guidance(), steered by "
                     "article_interest. No change is also a valid answer.")
        return "\n".join(lines)
    focus = lost[0]
    owners = [f"{name} ({where})"
              for name, _, where, codes in _PROMPT_LEDGER if focus in codes]
    lines.append(f"PROMPT FOCUS: {focus} lost {counts[focus]} draft(s); "
                 f"the prompts that produce it: {'; '.join(owners)}.")
    top = (details.get(focus) or Counter()).most_common(3)
    if top:
        lines.append("Gate findings behind it: "
                     + "; ".join(f"{d!r} x{n}" for d, n in top))
    return "\n".join(lines)


def checklist_step(status: dict[str, Any]) -> tuple[str, list[str]]:
    """
    The first doctrine checklist step that is not clean, plus its evidence.

    Deterministic, so the engine is told which step binds instead of
    re-deriving it from a status dump every hour. The order is the doctrine's:
    a later step is never worth work while an earlier one reads "no".
    """
    payout = status.get("payout") or {}
    rc = status.get("receipt_check") or {}
    wallet = status.get("wallet") or {}
    earnings = status.get("earnings") or {}

    if not payout.get("live"):
        return ("1 — the receive path is off, so every reader sees no way to pay", [
            f"payout.live = {payout.get('live')}",
            f"payout.blocked_reason = {payout.get('blocked_reason')!r}",
        ])

    rc_lines = [
        f"receipt_check.covered / published_total = "
        f"{rc.get('covered')} / {rc.get('published_total')}",
        f"receipt_check.coverage_complete = {rc.get('coverage_complete')} "
        "(None = this cycle observed nothing; read as unknown, not as true)",
        f"receipt_check.known_without_footer = {rc.get('known_without_footer')}",
        f"receipt_check.last_reason = {rc.get('last_reason')!r}",
    ]
    known = rc.get("known_without_footer") or 0
    if known:
        missing = [f"{m.get('views')} views: {m.get('title')}"
                   for m in (rc.get("missing") or [])[:3] if isinstance(m, dict)]
        return (f"1 — {known} published post(s) show readers no way to pay",
                rc_lines + [f"busiest offenders: {missing}"])
    if rc.get("agrees_with_backfill") is False:
        return ("1 — backfill's self-report disagrees with what readers see",
                rc_lines + [
                    f"backfill.remaining = {(status.get('backfill') or {}).get('remaining')}",
                    "the observation (receipt_check) is the half to believe",
                ])

    received = float(wallet.get("received_total_usd")
                     or earnings.get("received_total_usd") or 0)
    other = wallet.get("other_assets") or {}
    wallet_lines = [
        f"wallet.received_total_usd = {received}",
        f"wallet.other_assets = {other}",
        f"wallet.error = {wallet.get('error')!r}",
    ]
    if received > 0 or other:
        attr = status.get("attribution") or {}
        return ("2 — money has arrived; attribute it before changing anything else",
                rc_lines + wallet_lines + [
                    f"attribution.receipt_count = {attr.get('receipt_count')}",
                    f"attribution.by_archetype = {attr.get('by_archetype')}",
                    "read count beside every total: one receipt is not a trend",
                ])

    return ("4 — reach into a live receive path (doctrine Principle 5, step 3): "
            "publish more articles, in the shapes readers measurably prefer",
            ["receive path verified; wallet is a real $0.00, so the work is reach"]
            + rc_lines + wallet_lines + _reach_lines(status))


def _reach_lines(status: dict[str, Any]) -> list[str]:
    """What reach work steers on: output, what readers prefer, what blocks a post."""
    lines: list[str] = []
    stats = status.get("article_stats") or {}
    if stats:
        lines.append(
            f"article_stats: {stats.get('count')} posts, {stats.get('total_views')} "
            f"views, avg {stats.get('avg_views')}, best {stats.get('best_views')} "
            f"({stats.get('best_title')!r})"
        )
    interest = status.get("article_interest") or {}
    rows = [r for r in (interest.get("archetypes") or []) if isinstance(r, dict)]
    if rows:
        lines.append("article_interest (n = posts; a row under n=3 is noise): " + "; ".join(
            f"{r.get('archetype')} n={r.get('count')} avg={r.get('avg_engagement')}"
            for r in rows
        ))
        try:
            from bot.earning.devto_stats import preferred_archetypes
            lines.append(f"preferred_archetypes() = {preferred_archetypes(interest)}")
        except Exception as exc:
            lines.append(f"preferred_archetypes() unavailable: {exc}")
    rejects = status.get("article_rejects") or {}
    counts = rejects.get("counts") or {}
    if counts:
        ranked = sorted(counts.items(), key=lambda kv: -kv[1])
        lines.append(
            f"article_rejects.counts (drafts lost per gate; total {rejects.get('total')}): "
            + ", ".join(f"{k}={v}" for k, v in ranked)
        )
        lines.append(f"article_rejects.last = {rejects.get('last_reason')!r}: "
                     f"{rejects.get('last_detail')!r}")
    daily = status.get("article_daily") or {}
    if daily:
        lines.append(f"article_daily = {daily}")
    news = status.get("newsletter_daily") or {}
    if news:
        lines.append(f"newsletter last published {news.get('published_at')}, "
                     f"{news.get('published')} issues total")
    return lines


def _operations_lines(status: dict[str, Any]) -> list[str]:
    """Engine and error state: a cycle that cannot draft cannot publish."""
    lines: list[str] = []
    eng = status.get("llm_engine") or {}
    if eng:
        lines.append(
            f"llm_engine: serving={eng.get('serving')}, live={eng.get('live')}, "
            f"disabled_reason={eng.get('disabled_reason')}, calls={eng.get('calls')}"
        )
    errors = [str(e)[:200] for e in (status.get("errors") or [])][:5]
    if errors:
        lines.append(f"errors this cycle: {errors}")
    last = status.get("last_evolution") or {}
    if last.get("error"):
        lines.append(f"last evolution error: {str(last['error'])[:200]}")
    skipped = (status.get("backfill") or {}).get("skipped") or {}
    if skipped:
        lines.append(f"backfill.skipped: {len(skipped)} post(s), e.g. "
                     f"{str(next(iter(skipped.values())))[:120]}")
    return lines


def _status_digest(status: dict[str, Any]) -> str:
    """Small fields verbatim, large ones by name and size, runtime keys dropped."""
    out: list[str] = []
    for key, value in status.items():
        if key.startswith("_") or key in _STATUS_BAIT:
            continue
        raw = json.dumps(value, default=str)
        if len(raw) <= _STATUS_FIELD_MAX_BYTES:
            out.append(f"{key}: {raw}")
        else:
            out.append(f"{key}: <{len(raw)} bytes omitted; read the module that owns it>")
    return "\n".join(out)


def _doctrine_extract(path: str = _DOCTRINE_PATH) -> str:
    """Every principle heading plus the checklist and channel table, verbatim."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except Exception:
        return f"DOCTRINE: {path} could not be read this cycle."
    sections: dict[str, list[str]] = {}
    principles: list[str] = []
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            current = title if title in _DOCTRINE_SECTIONS else None
            if title.startswith("Principle"):
                principles.append(title)
            if current:
                sections[current] = []
            continue
        if current:
            sections[current].append(line)
    out = [f"DOCTRINE ({path}; the standing brief, it outranks local improvements).",
           "Principles:"] + [f"- {p}" for p in principles]
    for title in _DOCTRINE_SECTIONS:
        body = "\n".join(sections.get(title, [])).strip().strip("-").strip()
        if body:
            out.append(f"\n### {title}\n{body}")
    return "\n".join(out)


def prior_proposals(limit: int = _MAX_PRIOR_PROPOSALS) -> str:
    """Open evolve/* branches, newest first, deduplicated with a repeat count."""
    try:
        result = subprocess.run(
            ["git", "log", "--no-walk=sorted", "--format=@@%cs %s", "--name-only",
             "--glob=refs/remotes/origin/evolve/*", "--glob=refs/heads/evolve/*"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
    except Exception as exc:
        log.info("Prior proposals unavailable: %s", exc)
        return ""
    if result.returncode != 0:
        return ""
    return format_prior_proposals(result.stdout, limit)


def format_prior_proposals(log_text: str, limit: int = _MAX_PRIOR_PROPOSALS) -> str:
    """Render `git log --name-only` output as one line per distinct proposal."""
    seen: dict[str, dict[str, Any]] = {}
    for block in log_text.split("@@")[1:]:
        lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
        if not lines:
            continue
        date, _, subject = lines[0].partition(" ")
        summary = re.sub(r"^\S*\s*evolve v[\d.]+:\s*", "", subject).strip()
        files = sorted({f for f in lines[1:] if f != "version.txt"})
        entry = seen.setdefault(summary, {"date": date, "files": set(), "n": 0})
        entry["n"] += 1
        entry["files"].update(files)
    if not seen:
        return ""
    rows = [
        f"- {e['date']} {s}" + (f" (proposed {e['n']}x)" if e["n"] > 1 else "")
        + (f" [{', '.join(sorted(e['files']))}]" if e["files"] else "")
        for s, e in list(seen.items())[:limit]
    ]
    return ("PRIOR PROPOSALS (open review branches, none merged; do not repeat "
            f"them — {len(seen)} distinct):\n" + "\n".join(rows))


def _file_inventory() -> str:
    """Every editable file with its size, so the model can see what exists."""
    rows: list[str] = []
    for pat in ("bot/**/*.py", "config/*.json", "docs/*.md", "requirements.txt"):
        for path in sorted(Path(".").glob(pat)):
            if not path.is_file():
                continue
            key = path.as_posix()
            try:
                n = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
            except Exception:
                n = "?"
            mark = " (protected: never write)" if key in PROTECTED_FILES else ""
            rows.append(f"- {key}: {n} lines{mark}")
    return "FILE INVENTORY (these already exist):\n" + "\n".join(rows)


def _commit_message(version: str, summary: str, plan: dict[str, Any]) -> str:
    """Subject for the branch list, body with the rationale the reviewer needs."""
    body: list[str] = []
    for key in _RATIONALE_KEYS:
        value = plan.get(key)
        if isinstance(value, list):
            value = "\n".join(f"  - {v}" for v in value)
            if value:
                body.append(f"{key}:\n{value}")
        elif value:
            body.append(f"{key}: {value}")
    subject = f"🧬 evolve v{version}: {summary[:80]}"
    return subject + ("\n\n" + "\n".join(body) if body else "")


# ── File reading ─────────────────────────────────────────────────────────────

def _snapshot_priority(key: str) -> tuple[int, str]:
    """
    Order the snapshot so the budget is spent on files evolution can edit.

    Protected orchestrator files and the test suite are read last: the model is
    forbidden from writing them, so filling the budget with them starves the
    modules it is actually allowed to improve.
    """
    norm = key.replace("\\", "/")
    if norm in PROTECTED_FILES:
        return (3, norm)
    if norm.endswith("tests.py"):
        return (2, norm)
    # The prompt files lead: newsletter.py once fell past the budget, so the
    # digest prompt sat in OMITTED FILES and could never be upgraded.
    if norm in _PROMPT_FILES:
        return (0, norm)
    return (1, norm)


def _read_codebase(max_bytes: int, include_config: bool = True) -> str:
    patterns = ["bot/**/*.py", "requirements.txt"]
    if include_config:
        patterns.insert(1, "config/*.json")

    parts: list[str] = []
    seen: set[str] = set()
    omitted: list[str] = []
    total = 0
    for pat in patterns:
        for path in sorted(Path(".").glob(pat), key=lambda p: _snapshot_priority(str(p))):
            key = str(path)
            if key in seen or not path.is_file():
                continue
            seen.add(key)
            try:
                raw = path.read_text(encoding="utf-8", errors="replace")
                remaining = max_bytes - total
                if remaining <= 0:
                    log.info("Codebase snapshot full at %d bytes — skipping %s", max_bytes, key)
                    omitted.append(key)
                    continue
                if len(raw) > remaining:
                    raw = raw[:remaining] + "\n... [truncated]"
                parts.append(f"=== {key} ===\n{raw}")
                total += len(raw)
            except Exception as exc:
                parts.append(f"=== {key} === [unreadable: {exc}]")
    if omitted:
        parts.append(f"# OMITTED FILES (budget exceeded — do not propose changes to these): {omitted}")
    return "\n\n".join(parts) or "(no source files found)"


# ── Change application ────────────────────────────────────────────────────────

def _apply_changes(changes: list, max_changes: Any = None) -> list[dict]:
    if not isinstance(changes, list):
        return []
    try:
        limit = max(1, min(int(max_changes), MAX_CHANGES))
    except (TypeError, ValueError):
        limit = MAX_CHANGES
    applied: list[dict] = []
    for ch in changes[:limit]:
        if not isinstance(ch, dict):
            continue
        filepath = str(ch.get("file", "")).strip().lstrip("/")
        reason   = str(ch.get("reason", ""))

        if not filepath:
            log.warning("Skipping malformed change (missing file)")
            continue
        if filepath in PROTECTED_FILES:
            log.warning("Blocked write to protected orchestrator file: %s", filepath)
            continue
        if not _is_safe(filepath):
            log.warning("Blocked write to forbidden path: %s", filepath)
            continue
        if ch.get("edits") is not None:
            content = _apply_edits(filepath, ch["edits"])
        else:
            content = str(ch.get("content", "")).strip()
            if content and _truncates(filepath, content):
                log.warning("Refused rewrite of %s: it would drop %d%%+ of the file",
                            filepath, round((1 - _SHRINK_FLOOR) * 100))
                continue
        if not content:
            log.warning("Skipping change to %s (no content, or edits did not apply)", filepath)
            continue
        if filepath.endswith(".py") and not _is_valid_python(content):
            log.warning("Skipping file with Python syntax error: %s", filepath)
            continue

        original_backup = _backup(filepath)
        dest = Path(filepath)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        log.info("Wrote %s — %s", filepath, reason[:60])
        applied.append({"file": filepath, "reason": reason, "_backup": original_backup})

    return applied


def _apply_edits(filepath: str, edits: Any) -> str | None:
    """
    Apply search/replace pairs to an existing file, or None if any pair misses.

    All or nothing: an "old" that occurs zero times or more than once means the
    model is editing a file it did not read correctly, and applying the other
    pairs would leave a half-made change for the reviewer to untangle.
    """
    path = Path(filepath)
    if not path.is_file() or not isinstance(edits, list) or not edits:
        log.warning("Edits for %s skipped: file missing or no edits given", filepath)
        return None
    text = path.read_text(encoding="utf-8")
    for i, edit in enumerate(edits):
        if not isinstance(edit, dict):
            return None
        old, new = edit.get("old"), edit.get("new", "")
        if not isinstance(old, str) or not old or not isinstance(new, str):
            log.warning("Edit %d for %s is malformed", i, filepath)
            return None
        hits = text.count(old)
        if hits != 1:
            log.warning("Edit %d for %s: 'old' found %d times, need exactly 1",
                        i, filepath, hits)
            return None
        text = text.replace(old, new, 1)
    if text == path.read_text(encoding="utf-8"):
        return None
    return text


def _truncates(filepath: str, content: str) -> bool:
    """True when a full rewrite would keep too little of a large existing file."""
    path = Path(filepath)
    if not path.is_file():
        return False
    try:
        old_size = len(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return False
    return old_size >= _SHRINK_MIN_BYTES and len(content) < old_size * _SHRINK_FLOOR


# ── Verification & LLM fix ───────────────────────────────────────────────────

_FIX_SYSTEM = """\
You are a Python code repair agent for E-Evolve, a self-improving GitHub Actions bot.
A file you previously generated has an import/runtime error. Fix it.

Respond with ONLY a single JSON object — no markdown, no prose.

Schema:
{
  "content": "COMPLETE fixed file content — not a diff or snippet",
  "reason": "one-sentence description of what was wrong"
}

Rules:
1. Output the ENTIRE file, not just the changed lines
2. The fix must be syntactically valid Python
3. Do not remove existing functionality — only fix the error
4. Respect the config schema shown in the prompt"""


def _import_check(filepath: str) -> str | None:
    """
    Run `python -c "import <module>"` for bot/ .py files,
    or `python -m py_compile <file>` for others.
    Returns error string on failure, None on success.
    """
    path = Path(filepath)
    if not path.exists() or not filepath.endswith(".py"):
        return None

    if filepath.startswith("bot/") or filepath.startswith("bot\\"):
        # Convert path to module name: bot/earning/articles.py -> bot.earning.articles
        module = filepath.replace("\\", "/")
        if module.endswith(".py"):
            module = module[:-3]
        module = module.replace("/", ".")

        result = subprocess.run(
            [sys.executable, "-c", f"import {module}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    else:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            text=True,
            timeout=30,
        )

    if result.returncode != 0:
        err = (result.stderr or result.stdout or "unknown error").strip()
        return err[:800]
    return None


def _load_strategy_config() -> str:
    try:
        return Path("config/strategy.json").read_text(encoding="utf-8")
    except Exception:
        return "{}"


def _verify_and_fix(applied: list[dict], llm: Any, status: dict) -> list[dict]:
    """
    For each applied .py change, import-check it.
    On error: ask LLM to fix (up to MAX_FIX_RETRIES).
    On repeated failure: restore backup and drop from applied list.
    Returns the final list of successfully verified changes.
    """
    if not applied:
        return applied

    strategy_cfg = _load_strategy_config()
    verified: list[dict] = []

    for change in applied:
        filepath = change["file"]
        if not filepath.endswith(".py"):
            verified.append(change)
            continue

        error = _import_check(filepath)
        if error is None:
            log.info("Verification passed: %s", filepath)
            verified.append(change)
            continue

        log.warning("Verification FAILED for %s: %s", filepath, error[:120])

        fixed = False
        for attempt in range(1, MAX_FIX_RETRIES + 1):
            log.info("Fix attempt %d/%d for %s", attempt, MAX_FIX_RETRIES, filepath)
            try:
                current_content = Path(filepath).read_text(encoding="utf-8", errors="replace")
            except Exception:
                current_content = "(unreadable)"

            fix_prompt = (
                f"File: {filepath}\n\n"
                f"Error:\n{error}\n\n"
                f"Current (broken) content:\n{current_content}\n\n"
                f"Strategy config (for context):\n{strategy_cfg}\n\n"
                f"Bot status summary: version={status.get('version')}, "
                f"active_features={status.get('active_features', [])}\n\n"
                "Fix the file. JSON only."
            )
            try:
                fix_plan = llm.complete_json_for_role("upgrade", fix_prompt, system=_FIX_SYSTEM, max_tokens=_MAX_FIX_TOKENS)
                fixed_content = str(fix_plan.get("content", "")).strip()
                fix_reason    = str(fix_plan.get("reason", ""))
            except Exception as exc:
                log.warning("Fix LLM call failed attempt %d: %s", attempt, exc)
                continue

            if not fixed_content or not _is_valid_python(fixed_content):
                log.warning("Fix attempt %d produced invalid Python for %s", attempt, filepath)
                continue

            Path(filepath).write_text(fixed_content, encoding="utf-8")
            log.info("Applied fix attempt %d to %s: %s", attempt, filepath, fix_reason[:60])

            error = _import_check(filepath)
            if error is None:
                log.info("Verification passed after fix attempt %d: %s", attempt, filepath)
                change = {**change, "reason": f"{change.get('reason', '')} [fix: {fix_reason}]"}
                fixed = True
                break
            log.warning("Still failing after fix attempt %d: %s — %s", attempt, filepath, error[:80])

        if fixed:
            verified.append(change)
        else:
            log.error(
                "Could not fix %s after %d attempts — restoring backup",
                filepath, MAX_FIX_RETRIES,
            )
            _restore_backup(filepath, change.get("_backup"))

    return verified


def _restore_backup(filepath: str, original: str | None = None) -> None:
    """
    Restore filepath from the snapshot taken BEFORE this cycle touched it.

    `original` is that snapshot, recorded by _apply_changes. It must be used in
    preference to "the newest .bak", because every failed repair attempt used to
    take its own backup: the newest snapshot is then a broken fix, and restoring
    it left a truncated module on disk that crashed every importer. Falling back
    to the newest backup is only for a caller that has no recorded original.
    """
    src = Path(filepath)
    if original:
        candidate = Path(original)
        if candidate.exists():
            shutil.copy2(candidate, src)
            log.info("Restored %s from %s", filepath, candidate.name)
            return
        log.warning("Recorded backup %s for %s is gone — falling back to newest", original, filepath)

    bdir = Path(".evolution_backups")
    baks = sorted(bdir.glob(f"{src.name}.*.bak"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not baks:
        log.warning("No backup found for %s — leaving broken file in place", filepath)
        return
    shutil.copy2(baks[0], src)
    log.info("Restored %s from %s", filepath, baks[0].name)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_safe(p: str) -> bool:
    if ".." in p:
        return False
    for bad in FORBIDDEN_PREFIXES:
        if p.startswith(bad):
            return False
    for ok in ALLOWED_PREFIXES:
        if p.startswith(ok):
            return True
    return p in ("requirements.txt", "version.txt")


def _is_valid_python(src: str) -> bool:
    try:
        ast.parse(src)
        return True
    except SyntaxError as exc:
        log.warning("Syntax error in generated code: %s", exc)
        return False


def _backup(filepath: str) -> str | None:
    """Snapshot filepath and return the backup path, or None if there was nothing to copy."""
    src = Path(filepath)
    if not src.exists():
        return None
    bdir = Path(".evolution_backups")
    bdir.mkdir(exist_ok=True)
    # Microseconds, not seconds: two backups of the same file inside one second
    # used to collide on the same name, so the second silently overwrote the
    # first -- destroying the pre-cycle original this function exists to keep.
    ts   = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    dest = bdir / f"{src.name}.{ts}.bak"
    shutil.copy2(src, dest)
    # Prune: keep only newest 20 backups
    baks = sorted(bdir.glob("*.bak"), key=lambda p: p.stat().st_mtime)
    for stale in baks[:-20]:
        if stale != dest:
            stale.unlink()
    return str(dest)


def _resolve_version(proposed: Any, current: str) -> str:
    """Use proposed version if it's a valid X.Y.Z string; else bump patch."""
    if proposed and re.match(r"^\d+\.\d+\.\d+$", str(proposed).strip()):
        return str(proposed).strip()
    # Bump patch of current
    try:
        parts = [int(x) for x in current.split(".")]
        parts[2] += 1
        return ".".join(str(p) for p in parts)
    except Exception:
        return "1.0.1"


def _classify_error(error: str) -> str:
    s = error.lower()
    free_limit_markers = (
        "429",
        "rate_limit",
        "rate limit",
        "ratelimit",
        "resource_exhausted",
        "quota",
        "insufficient_quota",
        "too many requests",
        "free tier",
        "free-tier",
        "free limit",
        "free-limit",
        "daily limit",
        "tokens per day",
        "tpd",
        "requests per day",
        "rpd",
    )
    if any(marker in s for marker in free_limit_markers):
        return "free_limit"
    if "413" in s or "too large" in s or "request entity" in s:
        return "413"
    if "json" in s or "parse" in s or "decode" in s:
        return "json"
    return "api"


def _error_result(error: str, current_version: str) -> dict[str, Any]:
    error_type = _classify_error(error)
    return {
        "version_bumped_to": current_version,
        "summary":           f"Evolution skipped [{error_type}]: {error[:500]}",
        "changes_applied":   [],
        "suggestions":       [],
        "error":             error[:500],
        "error_type":        error_type,
    }
