from typing import Any
import requests
import time
from urllib.parse import quote_plus
import logging

log = logging.getLogger(__name__)

def _cell(row: dict[str, Any], key: str, default: Any = "") -> Any:
    """Safely get a value from a dict, returning default if missing or None."""
    val = row.get(key, default)
    return default if val is None else val

def _clean_list(items: list[str]) -> list[str]:
    """Clean a list of strings by stripping whitespace and removing empties."""
    return [item.strip() for item in items if item and item.strip()]

def _dicts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize a list of dicts, ensuring all values are JSON-serializable."""
    out: list[dict[str, Any]] = []
    for row in rows:
        clean: dict[str, Any] = {}
        for k, v in row.items():
            if v is None:
                clean[k] = ""
            elif isinstance(v, (str, int, float, bool)):
                clean[k] = v
            else:
                clean[k] = str(v)
        out.append(clean)
    return out

def _parse_reddit_rss(text: str, subreddit: str) -> list[dict[str, Any]]:
    """Parse Reddit RSS feed text and return leads."""
    # Stub implementation - should parse XML and extract leads
    log.debug("[code_techs] Parsing RSS for r/%s (stub)", subreddit)
    return []

def _fetch_reddit_leads(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """Fetch Reddit leads using RSS feeds.

    This function now respects the max_reddit_requests limit and includes
    proper error handling for rate limiting. It also logs the subreddit being
    queried for better debugging.
    """
    leads: list[dict[str, Any]] = []
    subreddits = _clean_list(cfg.get("reddit_subreddits", []))
    queries = _clean_list(cfg.get("reddit_searches", [])) or _clean_list(cfg.get("community_searches", []))
    max_requests = max(0, int(cfg.get("max_reddit_requests", 24) or 0))
    if not subreddits or not queries or max_requests <= 0:
        return leads

    headers = {
        "Accept": "application/atom+xml, application/rss+xml, text/xml;q=0.9",
        "User-Agent": "e-evolve-code-techs/1.0 read-only lead research",
    }
    backoff = max(0, int(cfg.get("reddit_backoff_seconds", 5) or 0))
    request_count = 0
    for index, subreddit in enumerate(subreddits):
        if request_count >= max_requests:
            break
        query = queries[index % len(queries)]
        request_count += 1
        url = (
            f"https://www.reddit.com/r/{quote_plus(subreddit)}/search.rss"
            f"?q={quote_plus(query)}&restrict_sr=1&sort=new"
        )
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code in (403, 429):
                log.info(
                    "[code_techs] Reddit throttled (%s) at r/%s; stopping Reddit for this cycle",
                    resp.status_code, subreddit
                )
                if backoff:
                    time.sleep(backoff)
                break
            resp.raise_for_status()
            leads.extend(_parse_reddit_rss(resp.text, subreddit))
        except Exception as exc:
            log.warning("[code_techs] Reddit search failed for r/%s %r: %s", subreddit, query, exc)
    return leads

def run(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """Run the code techs lead generation."""
    return _fetch_reddit_leads(cfg)