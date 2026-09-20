_DEFAULTS = {
        "max_articles_per_cycle": 1,
        # NOTE: articles gate on the calendar date (one per UTC day), not on an
        # elapsed interval, so strategy.json's articles.min_interval_hours is not
        # read here. It is left in the config file rather than silently honoured.
        "source_max_age_hours": 24,
        # How many past titles/sources to remember for duplicate detection.
        "history_limit": 200,
        "min_words": 700,
        # Follow-up behaviour: mine the best recent post for a deeper second article.
        "followup_enabled": True,
        "followup_window_hours": 48,
        "followup_min_views": 40,
        "title_min_chars": 25,
        "title_max_chars": 70,
        # How much a proven archetype is worth when ranking sources, in trending-score
        # points. Deliberately smaller than the authority gap between an edited
        # publisher and an open tag feed (see trending._AUTHORITY), so interest breaks
        # ties between comparable sources rather than promoting a weak one.
        "archetype_bonus": 12.0,
        "archetype_bonus_step": 4.0,
    }


def run(config: dict, state: dict, *, dry_run: bool = False) -> dict:
    """Run the articles earning cycle.

    Args:
        config: Strategy configuration dict (merged with _DEFAULTS).
        state: Persistent state dict loaded from disk.
        dry_run: If True, do not publish or mutate external state.

    Returns:
        Dict with keys: 'published' (list of article metadata),
        'skipped' (list of reasons), 'state' (updated state dict).
    """
    # Merge defaults with provided config
    cfg = {**_DEFAULTS, **config.get("articles", {})}

    # Initialize state if needed
    if "articles" not in state:
        state["articles"] = {
            "history": [],
            "last_published_date": None,
            "followup_candidates": [],
        }
    art_state = state["articles"]

    published = []
    skipped = []

    # Check daily limit (one per UTC day)
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).date().isoformat()
    if art_state.get("last_published_date") == today:
        skipped.append("daily_limit_reached")
        return {"published": published, "skipped": skipped, "state": state}

    if dry_run:
        skipped.append("dry_run")
        return {"published": published, "skipped": skipped, "state": state}

    # TODO: Implement actual article generation logic here
    # This would involve:
    # 1. Fetching trending sources
    # 2. Filtering by age, duplicates, etc.
    # 3. Generating article via LLM
    # 4. Publishing to Dev.to
    # 5. Updating state

    skipped.append("not_implemented")
    return {"published": published, "skipped": skipped, "state": state}