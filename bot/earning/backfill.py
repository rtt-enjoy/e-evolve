from __future__ import annotations

import logging
import os
import time
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
    already earns real traffic can silently degrade it, and no gate downstream
    would catch it, because the gates run on drafts and these are live posts.

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

        if not candidates:
            action["success"] = True
            action["_quiet"] = True
            state["last_reason"] = "nothing_to_do"
            state["last_run"] = datetime.now(timezone.utc).isoformat()
            state["remaining"] = 0
            log.info("[backfill] every published post already carries the footer")
            return action

        # Highest-traffic first: the whole point is the readers who are already
        # there, and the view distribution is extremely top-heavy.
        candidates.sort(key=lambda p: int(p.get("page_views") or 0), reverse=True)

        updated = 0
        for post in candidates[:int(cfg.get("max_per_cycle", 3))]:
            body = str(post.get("body_markdown") or "")
            footered = payout.add_footer({"body_markdown": body}, payout_cfg)
            new_body = str(footered.get("body_markdown") or "")
            # add_footer is a no-op when it decides the footer must be omitted.
            # Sending an unchanged body would spend a write for nothing.
            if new_body == body or not payout.has_footer(new_body, payout_cfg):
                continue

            # Retry loop for rate limits and transient errors
            success = False
            last_result = None
            for attempt in range(3):
                result = devto.update_body(int(post["id"]), new_body, key)
                if result.get("success"):
                    success = True
                    updated += 1
                    state.setdefault("done_ids", []).append(post["id"])
                    log.info("[backfill] footer added to %s (%s views)",
                             str(post.get("title", ""))[:60], post.get("page_views"))
                    break
                else:
                    error = result.get("error", "")
                    # If the error indicates a rate limit, back off and retry
                    if "429" in error or "Too Many Requests" in error:
                        sleep_time = 2 ** attempt  # exponential backoff
                        log.warning("[backfill] rate limited, retrying in %ds", sleep_time)
                        time.sleep(sleep_time)
                        continue
                    # Any other error stops trying this post
                    last_result = result
                    break
            if not success:
                # Record the failure for diagnostics
                state.setdefault("skipped", {})[str(post["id"])] = (
                    last_result.get("error", "") if last_result else "unknown"
                )
                # Stop the batch on the first non‑rate‑limit failure rather than
                # hammering a failing API.
                break

        limit = int(cfg.get("history_limit", 200))
        # done_ids is a set in spirit; dedupe before trimming so a post cannot
        # consume several slots of the bounded history.
        seen: set = set()
        deduped = []
        for i in state.get("done_ids", []):
            if i is not None and i not in seen:
                seen.add(i)
                deduped.append(i)
        state["done_ids"] = deduped[-limit:]
        state["updated_total"] = int(state.get("updated_total", 0)) + updated
        state["last_run"] = datetime.now(timezone.utc).isoformat()

        # `remaining` is the count the owner is told to read: posts that still
        # show readers no way to pay. It is only as honest as `candidates`,
        # which is why the body_markdown regression above mattered so much --
        # it drove this to 0 while every post lacked a footer.
        state["remaining"] = max(len(candidates) - updated, 0)
        state["last_reason"] = "updated" if updated else "update_failed"

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