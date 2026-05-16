"""
Earning Module — Crypto Auto-Payout (Binance → external wallet)

Activates with: BINANCE_API_KEY  BINANCE_SECRET_KEY  BINANCE_WITHDRAW_ADDRESS

Withdraws USDT to BINANCE_WITHDRAW_ADDRESS when accumulated profit since last
payout exceeds strategy.payout.min_payout_usd.

IMPORTANT: The destination address MUST be whitelisted in your Binance account
(Wallet → Withdraw → Address Book) before this will work. Binance rejects
withdrawals to non-whitelisted addresses via API.
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger(__name__)


def _load_strategy() -> dict:
    try:
        return json.loads(Path("config/strategy.json").read_text())
    except Exception:
        return {}


_strategy = _load_strategy().get("payout", {})
MIN_PAYOUT_USD   = float(_strategy.get("min_payout_usd", 20.0))
COIN             = str(_strategy.get("coin", "USDT"))
NETWORK          = str(_strategy.get("network", "BSC")).upper()
FEE_BUFFER_USD   = float(_strategy.get("fee_buffer_usd", 1.5))  # keep buffer for fees

_NETWORK_ADDRESS_HINTS = {
    "BSC": ("BNB Smart Chain", "0x"),
    "ETH": ("Ethereum", "0x"),
    "TRX": ("Tron", "T"),
}


@dataclass
class PayoutResult:
    platform: str = "binance_payout"
    success: bool = False
    withdrawn_usd: float = 0.0
    tx_id: Optional[str] = None
    address: Optional[str] = None
    error: Optional[str] = None
    skipped: bool = False
    skip_reason: Optional[str] = None
    estimated_usd: float = 0.0
    pnl_usd: float = 0.0


def run(llm: Any = None, status: dict[str, Any] = None) -> list[dict]:
    if status is None:
        status = {}

    api_key    = os.getenv("BINANCE_API_KEY",        "").strip()
    api_secret = os.getenv("BINANCE_SECRET_KEY",     "").strip()
    dest_addr  = os.getenv("BINANCE_WITHDRAW_ADDRESS","").strip()

    if not (api_key and api_secret and dest_addr):
        return []

    result = _maybe_withdraw(api_key, api_secret, dest_addr, status)
    if result.skipped:
        log.info("[payout] Skipped: %s", result.skip_reason)
    elif result.success:
        log.info("[payout] Withdrew $%.4f USDT → %s  tx=%s",
                 result.withdrawn_usd, result.address[:8] + "…", result.tx_id)
    else:
        log.warning("[payout] Failed: %s", result.error)

    return [vars(result)]


def _maybe_withdraw(api_key: str, api_secret: str,
                    dest_addr: str, status: dict) -> PayoutResult:
    address_error = _validate_destination(dest_addr)
    if address_error:
        return PayoutResult(error=address_error)

    try:
        from binance.client import Client
    except ImportError:
        return PayoutResult(error="python-binance not installed")

    # Check how much profit has accumulated since last payout
    earnings = status.get("earnings", {})
    total_earned   = float(earnings.get("total_usd", 0.0))
    last_payout_at = float(status.get("last_payout_total_usd", 0.0))
    profit_since   = round(total_earned - last_payout_at, 6)

    if profit_since < MIN_PAYOUT_USD:
        return PayoutResult(
            skipped=True,
            skip_reason=f"profit since last payout ${profit_since:.4f} < threshold ${MIN_PAYOUT_USD:.2f}",
        )

    try:
        client = Client(api_key, api_secret)
    except Exception as exc:
        return PayoutResult(error=f"Binance connect: {exc!s:.200}")

    # Check available USDT balance
    try:
        account   = client.get_account()
        usdt_free = _bal(account, COIN)
    except Exception as exc:
        return PayoutResult(error=f"balance fetch: {exc!s:.200}")

    # Keep fee buffer and a small trading reserve
    withdraw_usd = round(usdt_free - FEE_BUFFER_USD, 4)

    if withdraw_usd <= 0:
        return PayoutResult(
            skipped=True,
            skip_reason=f"USDT balance ${usdt_free:.4f} insufficient after fee buffer ${FEE_BUFFER_USD:.2f}",
        )

    # Cap withdrawal at the profit earned (don't drain trading capital)
    withdraw_usd = min(withdraw_usd, profit_since)

    if withdraw_usd <= 0:
        return PayoutResult(
            skipped=True,
            skip_reason=f"withdraw amount ${withdraw_usd:.4f} <= 0 after capping to profit",
        )

    try:
        resp = client.withdraw(
            coin=COIN,
            address=dest_addr,
            amount=withdraw_usd,
            network=NETWORK,
        )
        tx_id = resp.get("id", "unknown")
        # Record payout watermark in status so next cycle compares correctly
        status["last_payout_total_usd"] = total_earned
        status["last_payout_tx"]        = tx_id
        return PayoutResult(
            success=True,
            withdrawn_usd=withdraw_usd,
            tx_id=tx_id,
            address=dest_addr,
        )
    except Exception as exc:
        err = str(exc)[:300]
        # Binance error -3102 = address not whitelisted
        if "-3102" in err or "whitelist" in err.lower():
            err = (f"Address not whitelisted on Binance. "
                   f"Go to Wallet → Withdraw → Address Book and add {dest_addr[:12]}…")
        return PayoutResult(error=err)


def _bal(account: dict, asset: str) -> float:
    for b in account.get("balances", []):
        if b["asset"] == asset:
            return float(b["free"])
    return 0.0


def _validate_destination(dest_addr: str) -> Optional[str]:
    """Catch common Exodus/Binance network mismatches before withdrawal."""
    hint = _NETWORK_ADDRESS_HINTS.get(NETWORK)
    if not hint:
        known = ", ".join(sorted(_NETWORK_ADDRESS_HINTS))
        return f"Unsupported Exodus payout network {NETWORK!r}; use one of: {known}"

    network_name, prefix = hint
    if not dest_addr.startswith(prefix):
        return (f"{network_name} payout network expects an Exodus address "
                f"starting with {prefix!r}, got {dest_addr[:6]!r}")

    if prefix == "0x" and len(dest_addr) != 42:
        return (f"{network_name} payout address should be a 42-character "
                "0x address from Exodus")

    return None
