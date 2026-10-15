"""
Check for missing GitHub secrets and log warnings.

This module is imported by earning modules to surface configuration gaps
that prevent features from activating. It reads the status dict's
secret_readiness map and logs a warning for each inactive provider that
still has required secrets missing.
"""

import logging

log = logging.getLogger(__name__)


def log_missing_secrets(status: dict) -> None:
    """Emit a warning for every inactive provider with missing secrets."""
    readiness = status.get("secret_readiness") or {}
    for provider, info in readiness.items():
        if not info.get("active", False):
            missing = info.get("missing", [])
            if missing:
                log.warning(
                    "[%s] provider inactive due to missing secrets: %s",
                    provider.upper(),
                    ", ".join(missing),
                )