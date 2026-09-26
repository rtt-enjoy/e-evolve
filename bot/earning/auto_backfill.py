import os, requests, logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from . import devto_stats, payout

log = logging.getLogger("auto_backfill")

DEFAULTS = {
    "max_per_cycle": 3,
    "history_limit": 200,
}

def config() -> dict:
    from ._shared import load_config
    return load_config("backfill", DEFAULTS)

def _state(status: dict) -> dict:
    return status.setdefault("auto_backfill", {
        "done_ids": [],
        "skipped": {},
        "updated_total": 0,
        "last_run": None,
        "last_reason": None,
    })

def _fetch_published(api_key: str) -> List[Dict[str, Any]]:
    return devto_stats.fetch_published(api_key)

def _add_footer(body: str, cfg: dict) -> Dict[str, Any]:
    from .payout import add_footer
    return add_footer({"body_markdown": body}, cfg)

def _update_body(article_id: int, new_body: str, api_key: str) -> Dict[str, Any]:
    url = f"https://dev.to/api/articles/{article_id}"
    resp = requests.put(
        url,
        headers={"api-key": api_key, "Content-Type": "application/json", "Accept": "application/vnd.forem.api-v1+json"},
        json={"article": {"body_markdown": new_body}},
        timeout=30,
    )
    if resp.status_code == 200:
        return {"success": True, "url": resp.json().get("url", ""), "error": None}
    return {"success": False, "url": "", "error": resp.text[:200]}

def run(status=None) -> List[dict]:
    status = status or {}
    action = {"platform": "auto_backfill", "success": False, "updated": 0, "estimated_usd": 0.0}
    try:
        cfg = config()
        state = _state(status)
        api_key = os.getenv("DEV_TO_API_KEY", "").strip()
        if not api_key:
            action["error"] = "missing DEV_TO_API_KEY"
            return [action]
        if not payout.footer():
            action["error"] = "payout footer not live"
            return [action]
        posts = _fetch_published(api_key)
        if not posts:
            action["error"] = "no published posts"
            return [action]
        done = set(state.get("done_ids", []))
        candidates = [
            p for p in posts
            if p.get("id") is not None
            and p["id"] not in done
            and not payout.has_footer(p.get("body_markdown", ""), cfg)
        ]
        if not candidates:
            action["success"] = True
            action["_quiet"] = True
            state["last_reason"] = "nothing_to_do"
            state["last_run"] = datetime.now(timezone.utc).isoformat()
            state["remaining"] = 0
            log.info("[auto_backfill] all posts already have footer")
            return [action]
        candidates.sort(key=lambda x: int(x.get("page_views", 0)) or 0, reverse=True)
        updated = 0
        for post in candidates[: cfg.get("max_per_cycle", 3)]:
            body = post.get("body_markdown", "")
            new_body = _add_footer(body, cfg).get("body_markdown", "")
            if new_body == body or not payout.has_footer(new_body, cfg):
                continue
            res = _update_body(post["id"], new_body, api_key)
            if res["success"]:
                updated += 1
                state.setdefault("done_ids", []).append(post["id"])
                log.info("[auto_backfill] footer added to %s (%s views)",
                         post.get("title", "")[:60], post.get("page_views"))
            else:
                state.setdefault("skipped", {})[str(post["id"])] = res["error"]
                break
        limit = cfg.get("history_limit", 200)
        seen = set()
        deduped = []
        for i in state.get("done_ids", []):
            if i is not None and i not in seen:
                seen.add(i)
                deduped.append(i)
        state["done_ids"] = deduped[-limit:]
        state["updated_total"] = state.get("updated_total", 0) + updated
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        state["remaining"] = max(len(candidates) - updated, 0)
        state["last_reason"] = "updated" if updated else "update_failed"
        action["success"] = updated > 0
        action["updated"] = updated
        action["remaining"] = state["remaining"]
        if not updated:
            action["error"] = "no post could be updated"
        return [action]
    except Exception as e:
        log.warning("[auto_backfill] error: %s", e)
        action["error"] = str(e)[:200]
        return [action]

if __name__ == "__main__":
    import json, os
    status_json = os.getenv("STATUS_JSON", "{}")
    status = json.loads(status_json) if status_json else {}
    print(json.dumps(run(status), indent=2))