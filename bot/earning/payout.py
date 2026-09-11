"""
Payout module - handles the support footer and wallet address display.

This module manages the tip footer that gets appended to dev.to articles,
providing readers with a way to support the project via USDT on Tron.
"""
from __future__ import annotations

import logging
import os
from typing import Any

log = logging.getLogger(__name__)

# The wallet address is read from environment at runtime
_WALLET_ADDRESS = os.getenv("USDT_WALLET_ADDRESS", "").strip()
_NETWORK = "TRC-20 (Tron)"


def footer() -> str:
    """Return the standard tip footer for dev.to articles.
    
    The footer is appended to every published article, providing a clear
    path for readers to support the work with USDT on the Tron network.
    """
    if not _WALLET_ADDRESS:
        log.warning("USDT_WALLET_ADDRESS not set - footer will not include wallet")
        return ""
    
    return (
        f"\n\n---\n\n"
        f"**Support this work**\n\n"
        f"If this article saved you time or taught you something new, consider a small tip.\n"
        f"\n"
        f"**Network:** {_NETWORK}\n"
        f"**Address:** `{_WALLET_ADDRESS}`\n"
        f"\n"
        f"Any amount of USDT is appreciated. All contributions help sustain free content."
    )


def has_footer(body: str, cfg: dict[str, Any] | None = None) -> bool:
    """Check if a dev.to article body already contains the support footer.
    
    Args:
        body: The article body markdown to check
        cfg: Optional config (unused, kept for compatibility)
    
    Returns:
        True if the footer is present, False otherwise
    """
    if not body or not _WALLET_ADDRESS:
        return False
    return _WALLET_ADDRESS in body


def add_footer(article: dict[str, Any], cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Add the support footer to an article if not already present.
    
    Args:
        article: The article dict with 'body_markdown' key
        cfg: Optional config (unused, kept for compatibility)
    
    Returns:
        The article dict with footer added to body_markdown
    """
    if not article:
        return article
    
    body = str(article.get("body_markdown", ""))
    
    if has_footer(body, cfg):
        return article
    
    footer_text = footer()
    if footer_text:
        article["body_markdown"] = body.rstrip() + footer_text
        log.debug("Added support footer to article")
    
    return article


def config() -> dict[str, Any]:
    """Return the payout configuration.
    
    Returns:
        Dict with wallet address, network, and other payout settings
    """
    return {
        "enabled": bool(_WALLET_ADDRESS),
        "address": _WALLET_ADDRESS,
        "network": _NETWORK,
    }


def get_public_address() -> str:
    """Return the public wallet address for display.
    
    Returns:
        The wallet address or empty string if not configured
    """
    return _WALLET_ADDRESS


# For backwards compatibility with existing imports
__all__ = ["footer", "has_footer", "add_footer", "config", "get_public_address"]