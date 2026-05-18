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

from bot import github_secrets

log = logging.getLogger(__name__)

STATUS_FILE  = Path("status.json")
VERSION_FILE = Path("version.txt")

# feature name -> ALL secrets that must be non-empty to activate it.
#
# Runtime policy: secrets only activate LLM, research, and read-only status
# features. Publishing, posting, trading, minting, and payout keys are
# intentionally not feature activators, so their presence cannot trigger
# external side effects.
FEATURE_MAP: dict[str, list[str]] = {
    "llm_anthropic":   ["ANTHROPIC_API_KEY"],
    "llm_gemini":      ["GEMINI_API_KEY"],
    "llm_openrouter":  ["OPENROUTER_API_KEY"],
    "llm_groq":        ["GROQ_API_KEY"],
    "usdt_wallet":     ["USDT_WALLET_ADDRESS"],
}

LLM_ROLE_WORKFLOWS: dict[str, dict[str, str]] = {
    "upgrade": {
        "provider": "gemini",
        "model": "gemini-2.5-pro",
        "purpose": "research-only repair suggestions for Codex-owned code changes",
    },
    "research": {
        "provider": "openrouter",
        "model": "openrouter/free",
        "purpose": "RAG, market research, and earning-suggestion briefs",
    },
    "post": {
        "provider": "groq",
        "model": "llama-3.3-70b-versatile",
        "purpose": "draft-only suggestion text; no publishing or posting",
    },
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
    configured_secrets = _configured_secret_names()

    status["version"]           = version
    status["last_run"]          = datetime.now(timezone.utc).isoformat()
    status["total_runs"]        = int(status.get("total_runs", 0)) + 1
    status["active_features"]   = active
    status["inactive_features"] = inactive
    status["configured_github_secrets"] = sorted(configured_secrets)
    status["secret_readiness"]  = _secret_readiness(active, inactive, configured_secrets)
    status["llm_workflows"]     = _llm_workflows(active, configured_secrets)
    usdt_wallet = os.getenv("USDT_WALLET_ADDRESS", "").strip()
    if usdt_wallet:
        prev_balance = float(status.get("usdt_balance", 0.0))
        new_balance  = _fetch_usdt_balance(usdt_wallet)
        if new_balance is not None:
            status["usdt_balance"] = new_balance
            if new_balance > prev_balance:
                status["usdt_received"] = round(new_balance - prev_balance, 6)
                status["usdt_received_at"] = datetime.now(timezone.utc).isoformat()
            else:
                status.pop("usdt_received", None)
                status.pop("usdt_received_at", None)

    log.info("Cycle #%d | v%s | active=%s",
             status["total_runs"], version, active)
    return status


def save(status: dict[str, Any]) -> None:
    """Persist to status.json without runtime fields or secret values."""
    clean = sanitize_for_git(status)
    STATUS_FILE.write_text(json.dumps(clean, indent=2, default=str), encoding="utf-8")
    log.debug("status.json saved")


def sanitize_for_git(status: dict[str, Any]) -> dict[str, Any]:
    """Return a copy safe for tracked JSON files and public dashboard data."""
    secret_values = _secret_values()
    clean = _redact_secret_values(status, secret_values)
    if not isinstance(clean, dict):
        return {}

    clean.pop("usdt_wallet", None)
    return {k: v for k, v in clean.items() if not k.startswith("_")}


# ── Internals ───────────────────────────────────────────────────────────────

def _fetch_usdt_balance(address: str) -> float | None:
    """Query on-chain USDT balance. TRC-20 if address starts with T, else ERC-20."""
    import urllib.request
    import urllib.error
    try:
        if address.startswith("T"):
            # TRC-20 USDT via Tronscan public API (no key needed)
            url = f"https://apilist.tronscanapi.com/api/account/tokens?address={address}&token=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
            with urllib.request.urlopen(url, timeout=10) as r:
                data = json.loads(r.read())
            for tok in data.get("data", []):
                if tok.get("tokenId") == "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t":
                    return float(tok.get("quantity", 0)) / 1e6
            return 0.0
        elif address.startswith("0x"):
            # ERC-20 USDT via Etherscan (ETHERSCAN_API_KEY optional, free tier works without)
            contract  = "0xdac17f958d2ee523a2206206994597c13d831ec7"
            etherscan_key = os.getenv("ETHERSCAN_API_KEY", "YourApiKeyToken").strip()
            url = (f"https://api.etherscan.io/api?module=account&action=tokenbalance"
                   f"&contractaddress={contract}&address={address}&tag=latest&apikey={etherscan_key}")
            with urllib.request.urlopen(url, timeout=10) as r:
                data = json.loads(r.read())
            if data.get("status") == "1":
                return float(data["result"]) / 1e6
            return 0.0
        else:
            return None
    except Exception as exc:
        log.debug("USDT balance fetch failed: %s", exc)
        return None


def _defaults() -> dict[str, Any]:
    return {
        "version":           "1.0.0",
        "last_run":          None,
        "total_runs":        0,
        "active_features":   [],
        "inactive_features": list(FEATURE_MAP.keys()),
        "configured_github_secrets": [],
        "secret_readiness":  {},
        "llm_provider":      "unknown",
        "llm_roles":         {},
        "llm_workflows":     {},
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
        "article_daily": {
            "date":      None,
            "published": 0,
        },
        "suggestions":           [],
        "errors":                [],
        "usdt_wallet":           "",
        "usdt_balance":          0.0,
        "last_payout_total_usd": 0.0,
        "last_payout_tx":        None,
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


def _secret_values() -> list[str]:
    """Collect live secret values that must never be persisted."""
    secret_names = _secret_names()
    secret_names.update({
        "ETHERSCAN_API_KEY",
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "NFT_STORAGE_TOKEN",
    })
    return [
        value
        for name in secret_names
        if len(value := os.getenv(name, "").strip()) >= 8
    ]


def _secret_names() -> set[str]:
    names = {
        name
        for keys in FEATURE_MAP.values()
        for name in keys
        if any(marker in name for marker in ("KEY", "SECRET", "TOKEN", "PRIVATE", "WALLET"))
    }
    names.update({
        "ETHERSCAN_API_KEY",
        "GH_TOKEN",
        "GITHUB_TOKEN",
        "NFT_STORAGE_TOKEN",
    })
    return names


def _configured_secret_names() -> set[str]:
    """Configured names only; never reads or persists secret values."""
    names = github_secrets.configured_secret_names()
    names.update(
        name
        for name in _secret_names()
        if os.getenv(name, "").strip()
    )
    return names


def _redact_secret_values(value: Any, secret_values: list[str]) -> Any:
    if isinstance(value, dict):
        return {
            k: _redact_secret_values(v, secret_values)
            for k, v in value.items()
            if not str(k).startswith("_")
        }
    if isinstance(value, list):
        return [_redact_secret_values(item, secret_values) for item in value]
    if isinstance(value, str):
        redacted = value
        for secret in secret_values:
            redacted = redacted.replace(secret, "[redacted]")
        return redacted
    return value


def _secret_readiness(
    active: list[str],
    inactive: list[str],
    configured_secrets: set[str] | None = None,
    use_env: bool = True,
) -> dict[str, Any]:
    """Persist safe present/missing secret names for dashboard diagnostics."""
    active_set = set(active)
    configured = configured_secrets or set()
    readiness: dict[str, Any] = {}
    for feature, keys in FEATURE_MAP.items():
        # In CI, env tells us directly. During local dashboard regeneration, the
        # previous GitHub snapshot's active_features safely implies all keys for
        # that feature existed without exposing their values. Local runs can also
        # use GitHub's online secret names for readiness without reading values.
        present = [
            k for k in keys
            if (use_env and os.getenv(k, "").strip()) or k in configured or feature in active_set
        ]
        missing = [k for k in keys if k not in present]
        readiness[feature] = {
            "active": feature in active,
            "present": present,
            "missing": missing,
            "present_count": len(present),
            "required_count": len(keys),
        }
    return readiness


def _llm_workflows(
    active_features: list[str] | None = None,
    configured_secrets: set[str] | None = None,
) -> dict[str, Any]:
    """Describe role routing and whether each role can run this cycle."""
    active_set = set(active_features or [])
    configured = configured_secrets or set()
    workflows: dict[str, Any] = {}
    for role, cfg in LLM_ROLE_WORKFLOWS.items():
        provider = cfg["provider"]
        secret = {
            "gemini": "GEMINI_API_KEY",
            "groq": "GROQ_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
        }.get(provider)
        feature = f"llm_{provider}"
        workflows[role] = {
            **cfg,
            "active": bool(
                (secret and (os.getenv(secret, "").strip() or secret in configured))
                or feature in active_set
            ),
            "secret": secret,
        }
    return workflows
