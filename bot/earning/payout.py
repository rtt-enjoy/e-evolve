"""
Payout footer — the receive path appended to every published article.

The footer is appended inside ``devto.publish`` and inside the backfill path,
so it is one template in one place. It carries the validated Tron address the
wallet already reads, and nothing else.

The footer is intentionally simple: a blockquote with a heading, a note, and
the address in a code span so it is visible and copyable. No script, no
tracking, no external links.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from . import _shared

log = logging.getLogger(__name__)

DEFAULTS: dict[str, Any] = {
    "enabled": True,
    "heading": "Support this work",
    "note": "These write-ups are researched and published with no paywall, sponsor, or tracking. If one saved you an afternoon, a small tip keeps them coming.",
    "asset": "USDT, USDC or USDD",
    "address_env": "USDT_WALLET_ADDRESS",
    "network": "TRC-20 (Tron)",
}

def config() -> dict[str, Any]:
    """This module's slice of config/strategy.json, read at call time."""
    return _shared.load_config("payout", DEFAULTS)

def _address() -> str:
    """Return the published receive address, or '' when not configured."""
    cfg = config()
    env_name = str(cfg.get("address_env", "USDT_WALLET_ADDRESS") or "USDT_WALLET_ADDRESS")
    return os.getenv(env_name, "").strip()

def footer() -> str:
    """Return the footer markdown, or '' when payout is not live.

    Used as a boolean by the backfill module: any non-empty string means the
    footer is ready to append.
    """
    cfg = config()
    if not cfg.get("enabled", True):
        return ""
    address = _address()
    if not address:
        return ""
    return _render(cfg, address)

def _render(cfg: dict[str, Any], address: str) -> str:
    heading = str(cfg.get("heading", "Support this work"))
    note = str(cfg.get("note", ""))
    asset = str(cfg.get("asset", "USDT, USDC or USDD"))
    network = str(cfg.get("network", "TRC-20 (Tron)"))
    return (
        f"\n\n---\n\n"
        f"> **{heading}**\n"
        f">\n"
        f"> {note}\n"
        f">\n"
        f"> **Send a tip:** `{address}` ({network}, {asset})\n"
        f">\n"
        f"> If this article provided value, a small tip keeps these write-ups coming.\n"
    )

def has_footer(body: str, cfg: dict[str, Any] | None = None) -> bool:
    """True when the body already carries the payout footer."""
    cfg = cfg or config()
    if not cfg.get("enabled", True):
        return False
    address = _address()
    if not address:
        return False
    return address in body

def add_footer(article: dict[str, Any], cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append the footer to an article body if not already present."""
    cfg = cfg or config()
    if not cfg.get("enabled", True):
        return article
    body = str(article.get("body_markdown", ""))
    if has_footer(body, cfg):
        return article
    address = _address()
    if not address:
        return article
    article["body_markdown"] = body.rstrip() + _render(cfg, address)
    return article

def status() -> dict[str, Any]:
    """Public status fields for the dashboard."""
    cfg = config()
    address = _address()
    masked = address[:8] + "…" + address[-4:] if len(address) > 12 else address
    return {
        "enabled": bool(cfg.get("enabled", True)),
        "live": bool(address),
        "network": str(cfg.get("network", "TRC-20 (Tron)")),
        "address_masked": masked,
        "blocked_reason": None,
    }

def public() -> dict[str, Any]:
    """Publicly displayed payout information."""
    cfg = config()
    address = _address()
    return {
        "address": address,
        "network": str(cfg.get("network", "TRC-20 (Tron)")),
        "heading": str(cfg.get("heading", "Support this work")),
        "note": str(cfg.get("note", "")),
        "asset": str(cfg.get("asset", "USDT, USDC or USDD")),
    }