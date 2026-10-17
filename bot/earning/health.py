from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_HEALTH_FILE = Path("docs/health.json")

# Secrets this project needs to function, grouped by subsystem. A secret is
# REQUIRED only when its feature is active -- an inactive provider does not
# block the system, so the health check reports it as optional.
_REQUIRED_SECRETS = {
    "DEV_TO_API_KEY": "publishes articles and newsletters to dev.to",
    "ATRIA_API_KEY": "primary LLM provider for research, drafting, and upgrades",
    "GEMINI_API_KEY": "active LLM provider (Gemini)",
    "OPENROUTER_API_KEY": "active LLM provider and fallback chain",
    "GROQ_API_KEY": "active LLM provider",
    "USDT_WALLET_ADDRESS": "TRC-20 receive address for tips",
}

# Providers that are wired in but currently inactive. Their keys are optional
# until the owner activates them, so the health check lists them as
# "available_if_activated" rather than missing.
_OPTIONAL_SECRETS = {
    "ANTHROPIC_API_KEY": "Anthropic (Claude) LLM provider",
    "CEREBRAS_API_KEY": "Cerebras Cloud LLM provider",
    "GH_TOKEN": "GitHub token for repository searches",
}

# Active features from the last cycle. A feature is active when its provider
# is enabled in config and its key is present.
_ACTIVE_FEATURES = [
    "llm_atria",
    "llm_gemini",
    "llm_openrouter",
    "llm_groq",
    "usdt_wallet",
    "code_techs",
]

_INACTIVE_FEATURES = [
    "llm_anthropic",
    "llm_cerebras",
]


class HealthReport:
    """Collects health-check findings into a single serializable report."""

    def __init__(self) -> None:
        self.checked_at = datetime.now(timezone.utc).isoformat()
        self.secrets: dict[str, dict[str, Any]] = {}
        self.llm_providers: dict[str, dict[str, Any]] = {}
        self.devto: dict[str, Any] = {}
        self.wallet: dict[str, Any] = {}
        self.can_generate = False
        self.missing_required: list[str] = []
        self.all_required_secrets_present = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "checked_at": self.checked_at,
            "all_required_secrets_present": self.all_required_secrets_present,
            "can_generate": self.can_generate,
            "missing_required": self.missing_required,
            "secrets": self.secrets,
            "llm_providers": self.llm_providers,
            "devto": self.devto,
            "wallet": self.wallet,
        }


def _secret_status(name: str) -> dict[str, Any]:
    """Return presence/absence of a GitHub secret without leaking its value."""
    value = os.getenv(name, "").strip()
    return {
        "present": bool(value),
        "masked": f"{value[:4]}...{value[-4:]}" if len(value) >= 8 else "(set)" if value else None,
    }


def _check_secrets(report: HealthReport) -> None:
    """Check every required and optional secret, recording presence only."""
    for name, purpose in _REQUIRED_SECRETS.items():
        info = _secret_status(name)
        info["purpose"] = purpose
        info["required"] = True
        report.secrets[name] = info
        if not info["present"]:
            report.missing_required.append(name)
            report.all_required_secrets_present = False

    for name, purpose in _OPTIONAL_SECRETS.items():
        info = _secret_status(name)
        info["purpose"] = purpose
        info["required"] = False
        report.secrets[name] = info


def _check_llm_providers(report: HealthReport) -> None:
    """Map each LLM feature to its secret and active/inactive state."""
    provider_map = {
        "llm_atria": "ATRIA_API_KEY",
        "llm_gemini": "GEMINI_API_KEY",
        "llm_openrouter": "OPENROUTER_API_KEY",
        "llm_groq": "GROQ_API_KEY",
        "llm_anthropic": "ANTHROPIC_API_KEY",
        "llm_cerebras": "CEREBRAS_API_KEY",
    }
    for feature, secret_name in provider_map.items():
        active = feature in _ACTIVE_FEATURES
        present = bool(os.getenv(secret_name, "").strip())
        report.llm_providers[feature] = {
            "secret": secret_name,
            "active": active,
            "present": present,
            "usable": active and present,
        }


def _check_devto(report: HealthReport) -> None:
    """Check dev.to publishing readiness."""
    key = os.getenv("DEV_TO_API_KEY", "").strip()
    report.devto = {
        "api_key_present": bool(key),
        "can_publish": bool(key),
        "note": "Required for article and newsletter publishing to dev.to.",
    }


def _check_wallet(report: HealthReport) -> None:
    """Check USDT wallet configuration."""
    address = os.getenv("USDT_WALLET_ADDRESS", "").strip()
    report.wallet = {
        "address_present": bool(address),
        "network": "TRC-20 (Tron)" if address else None,
        "can_receive": bool(address),
        "note": "TRC-20 USDT receive address for tips and payouts.",
    }


def _compute_can_generate(report: HealthReport) -> None:
    """The bot can generate articles if dev.to key is set and at least one LLM provider is usable."""
    devto_ok = report.devto.get("can_publish", False)
    llm_ok = any(
        p.get("usable", False) for p in report.llm_providers.values()
    )
    report.can_generate = devto_ok and llm_ok


def run() -> dict[str, Any]:
    """Run all health checks and write docs/health.json.

    Returns the report dict. This is a read-only diagnostic: it inspect't make
    any network calls, mutate state, or contact any service. It only inspects
    environment variables and writes a JSON snapshot.
    """
    report = HealthReport()
    _check_secrets(report)
    _check_llm_providers(report)
    _check_devto(report)
    _check_wallet(report)
    _compute_can_generate(report)

    _HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    _HEALTH_FILE.write_text(
        json.dumps(report.to_dict(), indent=2, default=str),
        encoding="utf-8",
    )
    log.info("Health report written -> docs/health.json")
    return report.to_dict()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    result = run()
    print(json.dumps(result, indent=2))