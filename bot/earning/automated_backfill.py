'''"""Automated backfill script – processes all posts that lack the receive footer.

This script can be run manually or scheduled (e.g., via cron) to ensure that
all eligible posts are updated with the receive path without requiring a
manual command each cycle.
"""
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, List

from bot.earning import backfill, devto_stats

log = logging.getLogger("automated_backfill")

def run_all(status):
    """
    Run the backfill process for every published post that does not already
have the receive footer. This version processes the entire catalog in one
go, using a high `max_per_cycle` value to avoid hitting the per‑cycle limit.
    """
    # Load the latest status
    with open("status.json", "r", encoding="utf-8") as f:
        status = json.load(f)

    # Get dev.to API key from status
    api_key = status.get("devto_api_key", "")

    # Fetch all published posts
    published = devto_stats.fetch_published(api_key=api_key)

    # Collect candidates that need the footer
    candidates = []
    for post in published:
        if post.get("id") is None or "body_markdown" not in post:
            continue
        cfg = backfill.config()
        if backfill.needs_footer(post, cfg):
            candidates.append(post)

    if not candidates:
        log.info("No posts need backfill.")
        return

    # Allow processing all candidates by raising max_per_cycle
    cfg = backfill.config()
    cfg["max_per_cycle"] = 1000  # high enough for the whole list

    # Execute backfill
    action = backfill.run(llm=None, status=status, published=candidates)
    log.info("Automated backfill completed. Updated %d posts.", action.get("updated", 0))

def main():
    # Load status
    try:
        with open("status.json", "r", encoding="utf-8") as f:
            status = json.load(f)
    except Exception as e:
        log.error("Failed to load status.json: %s", e)
        return

    run_all(status)

if __name__ == "__main__":
    import json
    main()
'''