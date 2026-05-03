"""
Status Check — Phase 1
Loads persisted state and enriches it with live cycle data.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

STATUS_FILE  = Path("status.json")
VERSION_FILE = Path("version.txt")

# feature name → ALL secrets that must be non-empty to activate it
FEATURE_MAP: dict[str, list[str]] = {
    "llm_anthropic":   ["ANTHROPIC_API_KEY"],
    "llm_gemini":      ["GEMINI_API_KEY"],
    "llm_openrouter":  ["OPENROUTER_API_KEY"],
    "llm_groq":        ["GROQ_API_KEY"],
    "articles_devto":  ["DEV_TO_API_KEY"],
    "articles_medium": ["MEDIUM_INTEGRATION_TOKEN"],
    "twitter":         ["TWITTER_API_KEY", "TWITTER_API_SECRET",
                        "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET"],
    "crypto_binance":  ["BINANCE_API_KEY", "BINANCE_SECRET_KEY"],
    "nft_ethereum":    ["ETH_PRIVATE_KEY", "ETH_WALLET_ADDRESS"],
}


# ── Public API ──────────────────────────────────────────────────────────────

def load() -> dict[str, Any]:
    """Load status.json from disk. Returns clean defaults if missing/corrupt."""
    if STATUS_FILE.exists():
        try:
            data = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
            return _fill_defaults(data)
        except Exception as exc:
            corrupt_path = STATUS_FILE.with_suffix(".json.corrupt")
            try:
                STATUS_FILE.replace(corrupt_path)
                log.warning("status.json corrupt (%s) — saved to %s, using defaults", exc, corrupt_path)
            except Exception as mv_exc:
                log.warning("status.json corrupt (%s) — could not save backup (%s), using defaults", exc, mv_exc)
    return _defaults()


def snapshot(status: dict[str, Any]) -> dict[str, Any]:
    """Add live cycle data: timestamp, run counter, active features, version."""
    active   = [f for f, keys in FEATURE_MAP.items()
                if all(os.getenv(k, "").strip() for k in keys)]
    inactive = [f for f in FEATURE_MAP if f not in active]
    version  = VERSION_FILE.read_text().strip() if VERSION_FILE.exists() else "1.0.0"

    status["version"]           = version
    status["last_run"]          = datetime.now(timezone.utc).isoformat()
    status["total_runs"]        = int(status.get("total_runs", 0)) + 1
    status["active_features"]   = active
    status["inactive_features"] = inactive
    usdt_wallet = os.getenv("USDT_WALLET_ADDRESS", "").strip()
    if usdt_wallet:
        status["usdt_wallet"] = usdt_wallet

    log.info("Cycle #%d | v%s | active=%s",
             status["total_runs"], version, active)
    return status


def save(status: dict[str, Any]) -> None:
    """Persist to status.json, stripping all runtime-only keys (prefix _)."""
    clean = {k: v for k, v in status.items() if not k.startswith("_")}
    STATUS_FILE.write_text(json.dumps(clean, indent=2, default=str), encoding="utf-8")
    log.debug("status.json saved")


# ── Internals ───────────────────────────────────────────────────────────────

def _defaults() -> dict[str, Any]:
    return {
        "version":           "1.0.0",
        "last_run":          None,
        "total_runs":        0,
        "active_features":   [],
        "inactive_features": list(FEATURE_MAP.keys()),
        "llm_provider":      "unknown",
        "llm_roles":         {},
        "earnings": {
            "total_usd":       0.0,
            "this_week_usd":   0.0,
            "last_cycle_usd":  0.0,
            "week_started":    None,
            "breakdown":       {},
            "history":         [],
        },
        "last_evolution": {
            "summary":         "No evolution yet.",
            "changes_applied": [],
            "version_bumped_to": "1.0.0",
            "suggestions":     [],
        },
        "last_earning": {
            "actions":   [],
            "total_usd": 0.0,
        },
        "suggestions": [],
        "errors":      [],
    }


def _fill_defaults(data: dict[str, Any]) -> dict[str, Any]:
    """Backfill any missing keys from defaults without overwriting existing ones."""
    defaults = _defaults()
    for k, v in defaults.items():
        if k not in data:
            data[k] = v
        elif isinstance(v, dict) and isinstance(data.get(k), dict):
            for sk, sv in v.items():
                data[k].setdefault(sk, sv)
    return data
