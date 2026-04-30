"""
Shared utilities for earning modules.
"""
from __future__ import annotations

import re


def sanitize_tags(tags: list[str], max_tags: int = 4) -> list[str]:
    """Lowercase, strip to alphanumeric only (dev.to rejects hyphens in tags), deduplicate."""
    seen: set[str] = set()
    result: list[str] = []
    for tag in tags[:max_tags * 2]:
        clean = re.sub(r"[^a-z0-9]", "", tag.lower().replace(" ", "").replace("-", ""))
        clean = clean[:20]
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
        if len(result) >= max_tags:
            break
    return result
