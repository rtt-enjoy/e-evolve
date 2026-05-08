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
    "crypto_payout":   ["BINANCE_API_KEY", "BINANCE_SECRET_KEY", "BINANCE_WITHDRAW_ADDRESS"],
    "nft_ethereum":    ["ETH_PRIVATE_KEY", "ETH_WALLET_ADDRESS"],
}

LLM_ROLE_WORKFLOWS: dict[str, dict[str, str]] = {
    "think": {
        "provider": "gemini",
        "purpose": "evolution planning and code repair",
    },
    "fast": {
        "provider": "groq",
        "purpose": "article and thread generation",
    },
    "experiment": {
        "provider": "openrouter",
        "purpose": "alternate model experiments",
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

    status["version"]           = version
    status["last_run"]          = datetime.now(timezone.utc).isoformat()
    status["total_runs"]        = int(status.get("total_runs", 0)) + 1
    status["active_features"]   = active
    status["inactive_features"] = inactive
    status["secret_readiness"]  = _secret_readiness(active, inactive)
    status["llm_workflows"]     = _llm_workflows(active)
    usdt_wallet = os.getenv("USDT_WALLET_ADDRESS", "").strip()
    if usdt_wallet:
        status["usdt_wallet"] = usdt_wallet
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
    """Persist to status.json, stripping all runtime-only keys (prefix _)."""
    clean = {k: v for k, v in status.items() if not k.startswith("_")}
    STATUS_FILE.write_text(json.dumps(clean, indent=2, default=str), encoding="utf-8")
    log.debug("status.json saved")


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


def _secret_readiness(active: list[str], inactive: list[str], use_env: bool = True) -> dict[str, Any]:
    """Persist safe present/missing secret names for dashboard diagnostics."""
    active_set = set(active)
    readiness: dict[str, Any] = {}
    for feature, keys in FEATURE_MAP.items():
        # In CI, env tells us directly. During local dashboard regeneration, the
        # previous GitHub snapshot's active_features safely implies all keys for
        # that feature existed without exposing their values.
        present = [
            k for k in keys
            if (use_env and os.getenv(k, "").strip()) or feature in active_set
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


def _llm_workflows(active_features: list[str] | None = None) -> dict[str, Any]:
    """Describe role routing and whether each role can run this cycle."""
    active_set = set(active_features or [])
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
            "active": bool((secret and os.getenv(secret, "").strip()) or feature in active_set),
            "secret": secret,
        }
    return workflows
