'''Automation script to backfill missing footers on all published dev.to posts.

Runs via a GitHub Action nightly; processes all posts that lack the receive
path footer, adds the payout footer, and updates the post.

Usage (from CLI or CI):
    python -m bot.earning.automation_backfill --all
'''

import argparse
import logging
import os
from pathlib import Path

from ._shared import load_config
from .devto import update_body
from .payout import add_footer
from .devto_stats import fetch_published

log = logging.getLogger("automation_backfill")

def _add_footer(body: str, cfg: dict) -> str:
    """Add the payout footer to the given body."""
    footered = add_footer({"body_markdown": body}, cfg)
    return str(footered.get("body_markdown") or "")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Process all posts, not just new ones")
    args = parser.parse_args()

    cfg = load_config("backfill", {})
    api_key = os.getenv("DEV_TO_API_KEY")
    if not api_key:
        log.error("DEV_TO_API_KEY not set")
        return

    # Fetch all published posts
    posts = fetch_published(api_key=api_key)
    updated = 0

    for post in posts:
        post_id = post.get("id")
        if not post_id:
            continue

        body = str(post.get("body_markdown") or "")
        # Check if footer already present
        if "## Payout" in body:
            continue

        # Add footer
        new_body = add_footer({"body_markdown": body}, cfg)
        result = update_body(int(post_id), new_body, api_key)
        if result.get("success"):
            updated += 1
            log.info("Backfilled post %s", post.get("title", "unknown"))
        else:
            log.warning("Failed to backfill post %s: %s", post_id, result.get("error"))

    log.info("Backfill complete: %d posts updated", updated)

if __name__ == "__main__":
    main()