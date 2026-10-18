import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from ._shared import load_config

log = logging.getLogger("health_check")

TRC20_ADDRESS_PATTERN = re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$")

def _is_valid_tron_address(address: str) -> bool:
    return bool(TRC20_ADDRESS_PATTERN.match(address))

def _load_wallet_config() -> dict:
    env_addr = os.getenv("USDT_WALLET_ADDRESS")
    if env_addr:
        return {"address": env_addr, "source": "env"}
    try:
        wallet_cfg = load_config("wallet", {})
        address = wallet_cfg.get("address")
        if address:
            return {"address": address, "source": "config"}
    except Exception:
        pass
    return {"address": None, "source": "unknown"}

def _write_health_json(status: dict, file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(status, indent=2, default=str), encoding="utf-8")
    log.info("Wrote health status to %s", file_path)

def _write_health_summary(status: dict, file_path: Path) -> None:
    lines = [
        "# Health Summary",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Secrets",
        "",
    ]
    required_secrets = ["ATRIA_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY", "USDT_WALLET_ADDRESS"]
    missing = []
    for secret in required_secrets:
        present = os.getenv(secret, "").strip()
        if not present:
            missing.append(secret)
        status["secrets"][secret] = {"present": bool(present), "value": present}
    if missing:
        lines.append("**- Missing required secrets:**")
        for s in missing:
            lines.append(f"  - `{s}`")
    else:
        lines.append("- All required secrets are present.")
    lines.append("")
    lines.append("## LLM Providers")
    provider_status = {}
    for prov, key in [("atria", "ATRIA_API_KEY"), ("anthropic", "ANTHROPIC_API_KEY"),
                       ("gemini", "GEMINI_API_KEY"), ("openrouter", "OPENROUTER_API_KEY"),
                       ("groq", "GROQ_API_KEY"), ("cerebras", "CEREBRAS_API_KEY")]:
        key_val = os.getenv(key, "").strip()
        active = key_val != ""
        provider_status[prov] = "active" if active else "missing"
    lines.append("**- Provider status:**")
    for prov, state in provider_status.items():
        lines.append(f"  - {prov}: {state}")
    lines.append("")
    lines.append("## Wallet")
    wallet = _load_wallet_config()
    addr = wallet.get("address", "")
    if addr:
        if _is_valid_tron_address(addr):
            lines.append(f"- **Address:** `{addr}` (valid Tron address)")
        else:
            lines.append(f"- **Address:** `{addr}` (invalid format)")
    else:
        lines.append("- **Address:** *not configured*")
    lines.append("")
    lines.append("## Summary")
    all_good = not missing and wallet.get("address") and _is_valid_tron_address(wallet.get("address", ""))
    lines.append(f"- **Overall readiness:** {'✅ Ready' if all_good else '⚠️ Issues detected'}")
    lines.append("")
    lines.append("**Instructions:**")
    lines.append("1. Add any missing secrets as GitHub repository secrets.")
    lines.append("2. Verify the USDT wallet address is correct and starts with 'T'.")
    lines.append("3. Re‑run this script after fixes.")
    summary_path = file_path.parent / "health_summary.md"
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    log.info("Wrote health summary to %s", summary_path)

def main() -> None:
    status: dict = {
        "llm_providers": {},
        "secrets": {},
        "wallet": {},
        "devto_ready": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Secrets
    required_secrets = ["ATRIA_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY", "USDT_WALLET_ADDRESS"]
    for secret in required_secrets:
        val = os.getenv(secret, "")
        status["secrets"][secret] = {"present": bool(val), "value": val}
        if not val:
            status["llm_providers"]["missing"] = secret

    # Wallet
    wallet_cfg = _load_wallet_config()
    status["wallet"] = {
        "address_masked": wallet_cfg.get("address", "").replace(".", "•") if wallet_cfg.get("address") else "Not set",
        "network": "TRC-20",
        "valid_address": _is_valid_tron_address(wallet_cfg.get("address", "")) if wallet_cfg.get("address") else False,
        "balance_usd": 0.0,
    }
    status["wallet"]["address"] = wallet_cfg.get("address", "")

    # dev.to readiness
    dev_to_api = os.getenv("DEV_TO_API_KEY", "").strip()
    status["devto_ready"] = bool(dev_to_api)

    # Write outputs
    health_json_path = Path("docs/health.json")
    health_summary_path = Path("docs/health_summary.md")
    _write_health_json(status, health_json_path)
    _write_health_summary(status, health_summary_path)

if __name__ == "__main__":
    main()