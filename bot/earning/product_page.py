"""
Product page generator.

Writes docs/product.md with the validated receive address and a short
description, so the wallet is visible on a dedicated landing page -- not
only inside articles and the README. This is the "publish product landing
page" step from the evolution backlog.

No LLM call, no new secret beyond the payout config (which already holds
USDT_WALLET_ADDRESS). Runs on demand or from a scheduled workflow.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import payout
from ._shared import load_config

log = logging.getLogger(__name__)

_REPORT_FILE = Path("docs/product.md")

_DEFAULTS = {"enabled": True}


def _config() -> dict:
    """This module's slice of config/strategy.json, read at call time."""
    return load_config("product_page", _DEFAULTS)


def run(llm: Any = None, status: dict | None = None) -> list[dict]:
    """Generate and write docs/product.md.

    Follows the same run(llm, status) contract as every other earning
    product so the orchestrator can call it uniformly. llm is accepted
    and deliberately unused -- the page is a template, not a model output.

    Returns a one-element action list, or [] when disabled.
    """
    cfg = _config()
    if not cfg.get("enabled", True):
        return []

    action: dict[str, Any] = {
        "platform": "product-page",
        "success": False,
        "estimated_usd": 0.0,
    }
    try:
        content = _generate_content()
        if not content:
            action["error"] = "no content generated"
            return [action]

        _REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        _REPORT_FILE.write_text(content, encoding="utf-8")

        action["success"] = True
        action["title"] = "Product landing page updated"
        action["url"] = str(_REPORT_FILE)
        log.info("[product_page] wrote %s", _REPORT_FILE)
        return [action]
    except Exception as exc:
        log.warning("[product_page] failed: %s", exc)
        action["error"] = str(exc)[:200]
        return [action]


def _generate_content() -> str:
    """Build the markdown content for the product page."""
    address = _wallet_address()
    payout_cfg = _safe_payout_config()
    footer = _safe_footer()

    lines = [
        "# Product",
        "",
        "A single digital product, listed on free channels and sold for "
        "stablecoin to this wallet.",
        "",
        "## Support this work",
        "",
        "These write-ups are researched and published with no paywall, "
        "sponsor, or tracking. If one saved you an afternoon, a small tip "
        "keeps them coming.",
        "",
        f"**Address:** `{address}`",
        f"**Network:** {payout_cfg.get('network', 'TRC-20 (Tron)')}",
        f"**Asset:** {payout_cfg.get('asset', 'USDT')}",
        "",
        "### Why tip?",
        "",
        str(payout_cfg.get("note", "")).strip()
        or "Thank you for supporting independent research.",
        "",
        "---",
        "",
    ]

    if footer:
        lines.extend([
            "## Receive Path",
            "",
            "The same address above is appended to every article this project "
            "publishes to dev.to, so readers can tip directly from any post.",
            "",
            "### Wallet footer",
            "",
            "```",
            str(footer).strip(),
            "```",
            "",
        ])

    lines.extend([
        "## Articles",
        "",
        "Browse the latest articles on [dev.to](https://dev.to/robust_true_try).",
        "",
        f"_Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
    ])

    return "\n".join(lines)


def _wallet_address() -> str:
    """Return the validated receive address, or a clear placeholder."""
    address = os.getenv("USDT_WALLET_ADDRESS", "").strip()
    if address:
        return address
    try:
        cfg = payout.config()
        addr = str(cfg.get("address", "") or "")
        if addr:
            return addr
    except Exception:
        pass
    return "(USDT_WALLET_ADDRESS not configured)"


def _safe_payout_config() -> dict:
    try:
        return payout.config() or {}
    except Exception:
        return {}


def _safe_footer() -> str:
    try:
        return payout.footer() or ""
    except Exception:
        return ""