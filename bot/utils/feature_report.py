"""Utility to generate a concise report of active/inactive features.

The function ``get_feature_report`` reads the current status dictionary
and returns a mapping that can be consumed by dashboards or logs.
"""

from __future__ import annotations

from typing import Dict, List


def get_feature_report(status: Dict[str, object]) -> Dict[str, List[str]]:
    """Return a report of active and inactive features.

    Parameters
    ----------
    status:
        The status dictionary produced by the bot during a run.

    Returns
    -------
    Dict[str, List[str]]
        ``{"active": [...], "inactive": [...], "missing_secrets": {...}}``
    """
    active = status.get("active_features", [])
    inactive = status.get("inactive_features", [])
    missing = status.get("secret_readiness", {})
    missing_secrets: Dict[str, List[str]] = {
        k: v.get("missing", []) for k, v in missing.items() if v.get("missing")
    }
    return {
        "active": list(active),
        "inactive": list(inactive),
        "missing_secrets": missing_secrets,
    }

# Example usage when run as a script.
if __name__ == "__main__":  # pragma: no cover
    import json
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m bot.utils.feature_report <status.json>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        status = json.load(f)
    print(json.dumps(get_feature_report(status), indent=2))