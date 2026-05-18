"""Health‑check utilities for the E‑Evolve bot.

This module provides a simple function that can be imported by external
scripts or GitHub Actions to verify that the bot has all required secrets
and that its core modules are importable.  It is intentionally lightweight
and has no runtime side effects.
"""

from __future__ import annotations

import importlib
import os
from typing import Dict, List

# Mapping of feature name to the list of required secrets.
_FEATURE_SECRETS: Dict[str, List[str]] = {
    "llm_gemini": ["GEMINI_API_KEY"],
    "llm_openrouter": ["OPENROUTER_API_KEY"],
    "llm_groq": ["GROQ_API_KEY"],
    "articles_devto": ["DEV_TO_API_KEY"],
    "articles_medium": ["MEDIUM_INTEGRATION_TOKEN"],
    "twitter": [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_SECRET",
    ],
    "crypto_binance": ["BINANCE_API_KEY", "BINANCE_SECRET_KEY"],
    "crypto_payout": [
        "BINANCE_API_KEY",
        "BINANCE_SECRET_KEY",
        "BINANCE_WITHDRAW_ADDRESS",
    ],
    "nft_ethereum": ["ETH_PRIVATE_KEY", "ETH_WALLET_ADDRESS"],
}

# List of modules that must be importable for the bot to function.
_REQUIRED_MODULES = [
    "bot.llm",
    "bot.evolution",
    "bot.earning",
    "bot.dashboard",
    "bot.status",
]


def check_health() -> Dict[str, object]:
    """Return a dictionary describing the health of the bot.

    The returned mapping contains:

    * ``missing_secrets`` – a mapping from feature name to list of
      secrets that are not set.
    * ``import_errors`` – a mapping from module name to the exception
      message if the import failed.
    * ``all_ok`` – a boolean that is ``True`` only if all required
      secrets are present and all modules import cleanly.
    """
    missing: Dict[str, List[str]] = {}
    for feature, secrets in _FEATURE_SECRETS.items():
        not_set = [s for s in secrets if not os.getenv(s, "")]
        if not_set:
            missing[feature] = not_set

    import_errors: Dict[str, str] = {}
    for mod in _REQUIRED_MODULES:
        try:
            importlib.import_module(mod)
        except Exception as exc:  # pragma: no cover – import errors are rare
            import_errors[mod] = str(exc)

    all_ok = not missing and not import_errors
    return {
        "missing_secrets": missing,
        "import_errors": import_errors,
        "all_ok": all_ok,
    }

# If this file is executed directly, print a quick health report.
if __name__ == "__main__":  # pragma: no cover
    import json
    print(json.dumps(check_health(), indent=2))