"""
Health diagnostic for E-Evolve.

Checks required GitHub secrets, LLM provider availability, dev.to publishing
readiness, and wallet configuration. Writes docs/health.json for owners to
inspect and act upon.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bot.earning import devto_stats, payout, wallet_assets

log = logging.getLogger(__name__)

_REQUIRED_SECRETS = [
    "ATRIA_API_KEY",
    "GEMINI_API_KEY",
    "OPENROUTER_API_KEY",
    "GROQ_API_KEY",
    "CEREBRAS_API_KEY",
    "ANTHROPIC_API_KEY",
    "DEV_TO_API_KEY",
    "USDT_WALLET_ADDRESS",
]

_HEALTH_FILE = Path("docs/health.json")


def _secrets_present() -> tuple[list[str], list[str]]:
    """Return (present, missing) secret names."""
    present = []
    missing = []
    for name in _REQUIRED_SECRETS:
        val = os.getenv(name)
        if val and val.strip():
            present.append(name)
        else:
            missing.append(name)
    return present, missing


def _llm_providers_available(present: list[str]) -> list[str]:
    """Map secret names to provider identifiers."""
    mapping = {
        "ATRIA_API_KEY": "atria",
        "GEMINI_API_KEY": "gemini",
        "OPENROUTER_API_KEY": "openrouter",
        "GROQ_API_KEY": "groq",
        "CEREBRAS_API_KEY": "cerebras",
        "ANTHROPIC_API_KEY": "anthropic",
    }
    return [mapping[name] for name in present if name in mapping]


def _devto_ready() -> tuple[bool, str]:
    """Check if dev.to API key works by fetching own articles."""
    key = os.getenv("DEV_TO_API_KEY", "").strip()
    if not key:
        return False, "DEV_TO_API_KEY not set"
    try:
        articles = devto_stats.fetch_published(key)
        return True, ""
    except Exception as exc:
        return False, str(exc)[:200]


def _wallet_configured() -> tuple[bool, str]:
    """Verify USDT_WALLET_ADDRESS is present and looks like a Tron address."""
    addr = os.getenv("USDT_WALLET_ADDRESS", "").strip()
    if not addr:
        return False, "USDT_WALLET_ADDRESS not set"
    if not (addr.startswith("T") and len(addr) >= 34):
        return False, f"address does not look like a Tron TRC-20 address: {addr[:10]}..."
    return True, ""


def run() -> None:
    """Execute the health check and write docs/health.json."""
    present, missing = _secrets_present()
    providers = _llm_providers_available(present)
    devto_ok, devto_err = _devto_ready()
    wallet_ok, wallet_err = _wallet_configured()

    can_generate = not missing and devto_ok and wallet_ok

    record: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "secrets_present": present,
        "missing_required": missing,
        "llm_providers_available": providers,
        "devto_ready": devto_ok,
        "devto_error": devto_err if not devto_ok else None,
        "wallet_configured": wallet_ok,
        "wallet_error": wallet_err if not wallet_ok else None,
        "can_generate": can_generate,
    }

    _HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    _HEALTH_FILE.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")

    log.info(
        "[health] check completed: secrets %d present, %d missing; dev.to %s; wallet %s",
        len(present), len(missing), "OK" if devto_ok else "FAIL", "OK" if wallet_ok else "FAIL",
    )