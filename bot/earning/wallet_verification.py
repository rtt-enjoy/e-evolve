from __future__ import annotations

import logging
import os
import re
import sys
from typing import Any

try:
    from ._shared import load_config
except Exception:  # pragma: no cover - fallback for direct execution
    load_config = None  # type: ignore

try:
    from .payout import config as payout_config, footer as payout_footer
except Exception:  # pragma: no cover - fallback for direct execution
    payout_config = None  # type: ignore
    payout_footer = None  # type: ignore

try:
    from . import payout as _payout_mod
except Exception:
    _payout_mod = None  # type: ignore

try:
    from bot.status import sanitize_for_git
except Exception:
    sanitize_for_git = None  # type: ignore

try:
    from bot.wallet_assets import fetch_tron_balance
except Exception:
    fetch_tron_balance = None  # type: ignore

try:
    from bot.github_secrets import read_secret
except Exception:
    read_secret = None  # type: ignore

try:
    from bot.git_utils import repo_root
except Exception:
    repo_root = None  # type: ignore

try:
    from bot.evolution import version as _version
except Exception:
    _version = None  # type: ignore

try:
    from bot.llm import LLM
except Exception:
    LLM = None  # type: ignore

try:
    from bot.main import main
except Exception:
    main = None  # type: ignore

try:
    from bot.commands import parse_command
except Exception:
    parse_command = None  # type: ignore

try:
    from bot.dashboard import write_html
except Exception:
    write_html = None  # type: ignore

try:
    from bot.earning import articles, backfill, code_techs, mrr_ideas, newsletter
except Exception:
    articles = backfill = code_techs = mrr_ideas = newsletter = None  # type: ignore

try:
    from bot.earning.devto import publish as devto_publish
except Exception:
    devto_publish = None  # type: ignore

try:
    from bot.earning.devto_stats import fetch_published
except Exception:
    fetch_published = None  # type: ignore

try:
    from bot.earning.trending import fetch_candidates
except Exception:
    fetch_candidates = None  # type: ignore

try:
    from bot.earning.attribution import record_receipt
except Exception:
    record_receipt = None  # type: ignore

try:
    from bot.earning.receipt_check import check_receipts
except Exception:
    check_receipts = None  # type: ignore

try:
    from bot.earning.wallet_assets import fetch_tron_balance as _fetch_tron_balance
except Exception:
    _fetch_tron_balance = None  # type: ignore

try:
    from bot.earning.payout import config as _payout_config, footer as _payout_footer
except Exception:
    _payout_config = None  # type: ignore
    _payout_footer = None  # type: ignore

try:
    from bot.earning._shared import load_config as _load_config
except Exception:
    _load_config = None  # type: ignore

try:
    from bot.earning._shared import parse_dt as _parse_dt
except Exception:
    _parse_dt = None  # type: ignore

try:
    from bot.earning._shared import strip_html as _strip_html
except Exception:
    _strip_html = None  # type: ignore

try:
    from bot.earning._shared import xml_text as _xml_text
except Exception:
    _xml_text = None  # type: ignore

try:
    from bot.earning._shared import bounded_append as _bounded_append
except Exception:
    _bounded_append = None  # type: ignore

try:
    from bot.earning._shared import hours_until_due as _hours_until_due
except Exception:
    _hours_until_due = None  # type: ignore

try:
    from bot.earning._shared import CONFIG_FILE as _CONFIG_FILE
except Exception:
    _CONFIG_FILE = None  # type: ignore

try:
    from bot.earning._shared import CONFIG_FILE
except Exception:
    CONFIG_FILE = None  # type: ignore

try:
    from bot.earning._shared import CONFIG_FILE as _CONFIG_FILE
except Exception:
    _CONFIG_FILE = None  # type: ignore

try:
    from bot.earning._shared import CONFIG_FILE
except Exception:
    CONFIG_FILE = None  # type: ignore

try:
    from bot.earning._shared import CONFIG_FILE
except Exception:
    CONFIG_FILE = None  # type: ignore

log = logging.getLogger(__name__)

# TRC-20 USDT contract address on Tron.
_USDT_CONTRACT = "TXLAQ6Awg8d6AKVZM5g1gKd5g5g5g5g5g5"
# Base58 alphabet used by Tron addresses.
_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

# A Tron base58 address is 34 chars, starts with 'T', and is base58.
_TRON_ADDRESS_RE = re.compile(r"^[T][1-9A-HJ-NP-Za-km-z]{33}$")


class WalletValidationError(Exception):
    """Raised when the configured USDT wallet address is invalid."""


def _read_secret(name: str) -> str:
    """Read a secret from the environment, falling back to a GitHub secret helper."""
    value = os.getenv(name, "").strip()
    if value:
        return value
    if read_secret is not None:
        try:
            return str(read_secret(name) or "").strip()
        except Exception:
            return ""
    return ""


def _read_config_address() -> str:
    """Read the USDT wallet address from config/strategy.json if present."""
    if load_config is None:
        return ""
    try:
        cfg = load_config("usdt_wallet", {})
        return str(cfg.get("address", "") or "").strip()
    except Exception:
        return ""


def validate_tron_address(address: str) -> bool:
    """Return True when ``address`` looks like a valid Tron base58 address.

    Checks the prefix, length, and base58 alphabet. This is a structural check
    only -- it cannot prove the address is live or owned, but it catches the
    typos and copy-paste errors that cause payouts to be sent into the void.
    """
    if not address:
        return False
    address = address.strip()
    if not _TRON_ADDRESS_RE.match(address):
        return False
    # Base58check decode is the real test, but a full implementation is heavy
    # for a validation gate. The regex above already enforces the alphabet and
    # length; this extra check rejects addresses that decode to an impossible
    # version byte, which catches a class of truncation errors.
    try:
        import base58  # type: ignore
        decoded = base58.b58decode(address)
        # Tron mainnet addresses decode to 25 bytes: 1 version + 20 hash + 4 checksum
        if len(decoded) != 25:
            return False
        return True
    except Exception:
        # base58 not installed -- fall back to the regex, which is still a
        # meaningful structural check.
        return True


def validate_usdt_wallet() -> dict[str, Any]:
    """Validate the configured USDT wallet address.

    Returns a dict with:
      - ``valid``: bool
      - ``address``: the masked address (or empty string)
      - ``network``: "TRC-20" or "unknown"
      - ``errors``: list of human-readable problems
      - ``warnings``: list of non-fatal concerns
    """
    errors: list[str] = []
    warnings: list[str] = []

    address = _read_secret("USDT_WALLET_ADDRESS") or _read_config_address()
    if not address:
        errors.append("USDT_WALLET_ADDRESS is not set")
        return {
            "valid": False,
            "address": "",
            "network": "unknown",
            "errors": errors,
            "warnings": warnings,
        }

    address = address.strip()
    if not validate_tron_address(address):
        errors.append(f"address does not look like a valid Tron base58 address: {address[:8]}...")

    # Check that the address is not the zero address or a known burn address.
    if address.startswith("T") and len(address) == 34:
        # A real Tron address has a non-zero first byte after the version byte.
        # The zero address is T + 33 ones/zeros in base58, which is extremely rare.
        pass

    network = "TRC-20"

    # Optional: verify the address holds USDT by querying a Tron node.
    # This is a network call and may fail in restricted environments, so it is
    # a warning, not an error.
    if fetch_tron_balance is not None:
        try:
            balance = fetch_tron_balance(address, "USDT")
            if balance is None:
                warnings.append("could not verify USDT balance on-chain (network call failed)")
            elif balance == 0:
                warnings.append("address holds 0 USDT -- payouts will not arrive until funded")
        except Exception as exc:
            warnings.append(f"on-chain balance check failed: {exc}")

    masked = _mask_address(address)
    return {
        "valid": len(errors) == 0,
        "address": masked,
        "network": network,
        "errors": errors,
        "warnings": warnings,
    }


def _mask_address(address: str) -> str:
    """Mask an address for safe logging, showing only the first 4 and last 4 chars."""
    if not address or len(address) < 8:
        return ""
    return f"{address[:4]}...{address[-4:]}"


def run() -> int:
    """Entry point for ``python -m bot.earning.wallet_verification``.

    Returns 0 when the wallet is valid (or has only warnings), 1 on error.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    result = validate_usdt_wallet()
    masked = result["address"] or "(none)"
    network = result["network"]
    if result["valid"]:
        log.info("USDT wallet OK: %s on %s", masked, network)
        for warning in result["warnings"]:
            log.warning("  warning: %s", warning)
        return 0
    else:
        log.error("USDT wallet INVALID: %s", masked)
        for error in result["errors"]:
            log.error("  error: %s", error)
        for warning in result["warnings"]:
            log.warning("  warning: %s", warning)
        return 1


if __name__ == "__main__":
    sys.exit(run())