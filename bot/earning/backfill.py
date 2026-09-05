"""
Put the receive path onto the articles that already have the readers.

``payout`` closed the structural zero for everything published *from now on*.
It did nothing for what was already out there, because the footer is attached
inside ``devto.publish`` and that is a POST -- it only ever runs on a new post.

At the time this was written that omission was most of the audience. The
account held 11 published articles carrying 1,949 lifetime views, and one of
them alone held 1,652 of them -- 85% of every reader this project has ever had
was looking at a post with no way to pay. New publishing adds roughly 177 views
per article, so it would take eleven consecutive perfect publishing days just to
match the reach that already exists and keeps accruing: those posts are
evergreen search traffic, which is why one of them is eight times the size of
anything published since.

Scored against Principle 2 of the doctrine this is the strongest channel left:

- **No new secret.** ``DEV_TO_API_KEY`` already publishes and already reads
  stats. ``PUT /api/articles/{id}`` takes the same key, and Forem scopes the
  lookup to the key's own articles.
- **No owner action**, per post or at all.
- **Within policy.** Editing our own article is publishing, which is the one
  outward action this project explicitly allows. Nothing is sent to anybody.
- **Verifiable on-chain**, like every other tip.
- **Reuses output already produced** -- no new writing, no new LLM call, no new
  maintenance surface.

Three rules hold it together.

**It never edits prose.** The only mutation is appending the same deterministic
footer ``payout`` already renders. There is no LLM call here, for the same
reason there is none in ``payout``: a model rewriting a post that earns real
traffic can silently degrade it, and no gate downstream would catch it, because
the gates run on drafts and these are live posts.

**A post whose body it cannot safely reproduce is skipped.** A dev.to body that
opens with YAML front matter has its title and tags re-read from that block on
save, and Forem's tag handling clears the existing list first. Nothing this bot
publishes uses front matter, but "probably not" is not a safe basis for
rewriting the account's best post, so those are detected and left alone.

**Editing does not re-surface a post.** Forem preserves ``published_at`` on
update, so this does not push old posts back into the feed and does not
counterfeit the follow-up path. It adds an ask to what people already read.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from . import _shared, devto, devto_stats, payout

log = logging.getLogger(__name__)

DEFAULTS: dict[str, Any] = {
    "enabled": True,
    # Per cycle, not total. The back catalogue is small and this is bounded
    # work, but a cap keeps one bad cycle from touching every post at once and
    # stays well clear of Forem's article-update rate limit.
    "max_per_cycle": 3,
    "history_limit": 200,
}


def config() -> dict[str, Any]:
    """This module's slice of config/strategy.json, read at call time."""
    return _shared.load_config("backfill", DEFAULTS)


def _state(status: dict) -> dict:
    return status.setdefault("backfill", {
        "done_ids": [],
        "skipped": {},
        "updated_total": 0,
        "last_run": None,
        "last_reason": None,
    })


def needs_footer(post: dict, cfg: dict[str, Any] | None = None) -> bool:
    """True when this published post has a usable body and carries no ask yet.

    ``has_footer`` is asked about the *live* body rather than trusting local
    history, so a post edited by hand on dev.to is read as it actually is.
    """
    body = str(post.get("body_markdown") or "")
    if not body.strip():
        return False
    if devto.has_front_matter(body):
        return False
    return not payout.has_footer(body, cfg)


def run(llm: Any = None, status: dict | None = None) -> list[dict]:
    """Product entry point: ``run(llm, status)``, like every other product.

    ``llm`` is accepted and deliberately unused. This module must never make a
    model call -- the footer is a template, and a model rewriting a post that
    already earns real traffic can degrade it with nothing downstream to catch
    it. The parameter exists only so the orchestrator can call this module the
    same way it calls the others.

    Returns a list of action dicts, or ``[]`` when there was nothing to do, so
    an idle cycle does not pad ``last_earning`` with noise.
    """
    status = status if isinstance(status, dict) else {}
    action = _run(status, os.getenv("DEV_TO_API_KEY", ""))
    # Nothing to report when the path is simply already complete or switched
    # off; those are states, not actions.
    if action.get("_quiet"):
        return []
    action.pop("_quiet", None)
    return [action]


def _run(status: dict, api_key: str = "", published: list | None = None) -> dict:
    """Append the support footer to already-published posts that lack one.

    ``published`` is the article list ``articles._refresh_stats`` already
    fetched this cycle; passing it in avoids a second identical API call. When
    omitted the list is fetched here, so the module also works standalone.

    Returns an action dict. Never raises: these posts are already live and
    already earning their reach, so a failure here must cost nothing but itself.
    """
    action: dict[str, Any] = {
        "platform": "dev.to-backfill",
        "success": False,
        "updated": 0,
        # Money is on-chain only. A footer added to an old post is an ask, not
        # a receipt, exactly as it is on a fresh publish.
        "estimated_usd": 0.0,
    }
    try:
        cfg = config()
        state = _state(status)

        if not cfg.get("enabled"):
            action["error"] = "disabled in config"
            action["_quiet"] = True
            state["last_reason"] = "disabled"
            return action

        # The footer decides whether there is an ask to add at all. If payout is
        # off, unconfigured, or holding an invalid address, there is nothing to
        # backfill and this must not invent one.
        if not payout.footer():
            action["error"] = "payout footer not live"
            action["_quiet"] = True
            state["last_reason"] = "payout_not_live"
            return action

        key = (api_key or "").strip()
        if not key:
            action["error"] = "no dev.to api key"
            action["_quiet"] = True
            state["last_reason"] = "no_key"
            return action

        posts = published if published is not None else devto_stats.fetch_published(key)
        if not posts:
            action["error"] = "no published posts available"
            action["_quiet"] = True
            state["last_reason"] = "no_posts"
            return action

        payout_cfg = payout.config()
        done = {i for i in state.get("done_ids", []) if i is not None}
        candidates = [
            p for p in posts
            if p.get("id") is not None
            and p.get("id") not in done
            and needs_footer(p, payout_cfg)
        ]

        # Diagnostic logging: explain exactly why the queue is empty.
        if not candidates:
            total = len(posts)
            with_footer = sum(1 for p in posts if not needs_footer(p, payout_cfg))
            front_matter = sum(1 for p in posts if devto.has_front_matter(str(p.get("body_markdown") or "")))
            no_body = sum(1 for p in posts if not str(p.get("body_markdown") or "").strip())
            log.info("[backfill] candidate scan: %d total posts, %d already have footer, %d skipped for front matter, %d have no body, %d candidates",
                     total, with_footer, front_matter, no_body, len(candidates))
            action["success"] = True
            action["_quiet"] = True
            state["last_reason"] = "nothing_to_do"
            state["last_run"] = datetime.now(timezone.utc).isoformat()
            state["remaining"] = 0
            return action

        # Highest-traffic first: the whole point is the readers who are already
        # there, and the view distribution is extremely top-heavy.
        candidates.sort(key=lambda p: int(p.get("page_views") or 0), reverse=True)

        log.info("[backfill] %d candidate(s) found, processing up to %d",
                 len(candidates), int(cfg.get("max_per_cycle", 3)))

        updated = 0
        for post in candidates[:int(cfg.get("max_per_cycle", 3))]:
            body = str(post.get("body_markdown") or "")
            footered = payout.add_footer({"body_markdown": body}, payout_cfg)
            new_body = str(footered.get("body_markdown") or "")
            # add_footer is a no-op when it decides the footer must be omitted.
            # Sending an unchanged body would spend a write for nothing.
            if new_body == body or not payout.has_footer(new_body, payout_cfg):
                log.info("[backfill] skipped post %s: footer could not be added", str(post.get("title", ""))[:60])
                continue

            result = devto.update_body(int(post["id"]), new_body, key)
            if result.get("success"):
                updated += 1
                state.setdefault("done_ids", []).append(post["id"])
                log.info("[backfill] footer added to %s (%s views)",
                         str(post.get("title", ""))[:60], post.get("page_views"))
            else:
                state.setdefault("skipped", {})[str(post["id"])] = result.get("error", "")
                # Stop on the first failure rather than hammering a failing API.
                log.warning("[backfill] update failed for post %s: %s", post["id"], result.get("error", ""))
                break

        limit = int(cfg.get("history_limit", 200))
        state["done_ids"] = state.get("done_ids", [])[-limit:]
        state["updated_total"] = int(state.get("updated_total", 0)) + updated
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        state["last_reason"] = "updated" if updated else "update_failed"
        state["remaining"] = max(len(candidates) - updated, 0)

        action["success"] = updated > 0
        action["updated"] = updated
        action["remaining"] = state["remaining"]
        if not updated:
            action["error"] = "no post could be updated"
        return action
    except Exception as exc:                       # pragma: no cover - defensive
        log.warning("[backfill] skipped: %s", exc)
        action["error"] = str(exc)[:200]
        return action