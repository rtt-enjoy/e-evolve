"""Health diagnostic module.

Checks required secrets, LLM provider availability, dev.to publishing
readiness, and wallet configuration. Writes a report to docs/health.json.
Can be run standalone: python -m bot.earning.health
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_REPORT_FILE = Path("docs/health.json")

# Required secrets for the active features. Missing any one of these means
# the bot cannot do its core work.
_REQUIRED_SECRETS: dict[str, str] = {
    "ATRIA_API_KEY": "LLM provider (atria) - primary model for article writing",
    "GEMINI_API_KEY": "LLM provider (gemini) - fallback for article writing",
    "OPENROUTER_API_KEY": "LLM provider (openrouter) - fallback for article writing",
    "GROQ_API_KEY": "LLM provider (groq) - fallback for article writing",
    "USDT_WALLET_ADDRESS": "USDT wallet receive address (TRC-20) for tips",
    "DEV_TO_API_KEY": "dev.to API key for publishing articles",
}

# Optional secrets that unlock inactive features. Their absence is reported
# but does not block core functionality.
_OPTIONAL_SECRETS: dict[str, str] = {
    "ANTHROPIC_API_KEY": "LLM provider (anthropic) - additional fallback",
    "CEREBRAS_API_KEY": "LLM provider (cerebras) - high-speed fallback",
}

# Tron address validation: starts with T, 34 chars, base58 alphabet.
_TRON_RE = re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$")


def _check_secret(name: str) -> dict[str, Any]:
    """Check if a secret is present in the environment."""
    value = os.getenv(name, "").strip()
    return {
        "name": name,
        "present": bool(value),
        "masked": _mask(value) if value else None,
    }


def _mask(value: str) -> str:
    """Mask a secret, showing only the first 4 and last 4 characters."""
    if len(value) <= 8:
        return "***"
    return value[:4] + "…" + value[-4:]


def _check_llm_provider(name: str, secret_name: str) -> dict[str, Any]:
    """Check if an LLM provider is configured."""
    present = bool(os.getenv(secret_name, "").strip())
    return {
        "provider": name,
        "active": present,
        "secret_name": secret_name,
        "present": present,
    }


def _check_wallet() -> dict[str, Any]:
    """Check the USDT wallet configuration."""
    address = os.getenv("USDT_WALLET_ADDRESS", "").strip()
    valid = bool(_TRON_RE.match(address))
    return {
        "configured": valid,
        "address_masked": _mask(address) if valid else None,
        "network": "TRC-20 (Tron)" if valid else None,
        "valid_format": valid,
    }


def _check_devto() -> dict[str, Any]:
    """Check dev.to publishing readiness."""
    key = os.getenv("DEV_TO_API_KEY", "").strip()
    return {
        "api_key_present": bool(key),
        "ready": bool(key),
    }


def _get_version() -> str:
    """Read the current version from version.txt."""
    try:
        return Path("version.txt").read_text(encoding="utf-8").strip()
    except Exception:
        return "unknown"


def run() -> dict[str, Any]:
    """Run the health diagnostic and write the report to docs/health.json.

    Returns the report dictionary. Also writes the report to disk so it can
    be inspected after a cycle.
    """
    # Required secrets
    required = {name: _check_secret(name) for name in _REQUIRED_SECRETS}
    missing_required = [name for name, info in required.items() if not info["present"]]

    # Optional secrets
    optional = {name: _check_secret(name) for name in _OPTIONAL_SECRETS}
    missing_optional = [name for name, info in optional.items() if not info["present"]]

    # LLM providers
    llm_providers = {
        "atria": _check_llm_provider("atria", "ATRIA_API_KEY"),
        "gemini": _check_llm_provider("gemini", "GEMINI_API_KEY"),
        "openrouter": _check_llm_provider("openrouter", "OPENROUTER_API_KEY"),
        "groq": _check_llm_provider("groq", "GROQ_API_KEY"),
        "anthropic": _check_llm_provider("anthropic", "ANTHROPIC_API_KEY"),
        "cerebras": _check_llm_provider("cerebras", "CEREBRAS_API_KEY"),
    }
    active_providers = sorted([name for name, info in llm_providers.items() if info["active"]])
    inactive_providers = sorted([name for name, info in llm_providers.items() if not info["active"]])

    # Wallet
    wallet = _check_wallet()

    # dev.to
    devto = _check_devto()

    # Overall readiness
    all_required_present = not missing_required
    can_generate = all_required_present and devto["ready"] and wallet["configured"]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "version": _get_version(),
        "all_required_secrets_present": all_required_present,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "required_secrets": required,
        "optional_secrets": optional,
        "llm_providers": llm_providers,
        "active_providers": active_providers,
        "inactive_providers": inactive_providers,
        "wallet": wallet,
        "devto": devto,
        "can_generate": can_generate,
    }

    _REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_FILE.write_text(
        json.dumps(report, indent=2, default=str),
        encoding="utf-8",
    )
    log.info("Health report written to %s", _REPORT_FILE)
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run()
    print(json.dumps(result, indent=2, default=str))