from __future__ import annotations

import logging
import os
from typing import Any

log = logging.getLogger(__name__)


def wallet_address() -> str:
	"""The USDT/USDC receive address this project publishes, or ''."""
	return os.getenv("USDT_WALLET_ADDRESS", "").strip()


def footer(cfg: dict[str, Any] | None = None) -> str:
	"""The deterministic support footer appended to every published artifact.

	One template, used by payout, backfill, and any future product surface so the
	receive path never drifts between the article, the README, and the release
	notes. Returns '' when no address is configured, so a missing secret cannot
	produce a footer that points nowhere.
	"""
	address = wallet_address()
	if not address:
		log.debug("[wallet_footer] no USDT_WALLET_ADDRESS set -- footer suppressed")
		return ""
	return (
		"\n\n---\n\n"
		"These write-ups are researched and published with no paywall, sponsor, or "
		"tracking. If one saved you an afternoon, a small tip keeps them coming.\n\n"
		f"USDT / USDC on TRC-20: `{address}`\n"
	)


def has_footer(body: str, cfg: dict[str, Any] | None = None) -> bool:
	"""True when ``body`` already carries the wallet footer."""
	return wallet_address() in str(body or "")


def add_footer(article: dict[str, Any], cfg: dict[str, Any] | None = None) -> dict[str, Any]:
	"""Append the wallet footer to an article dict's body_markdown.

	A no-op when no address is configured or the footer is already present, so
	calling it twice is safe and a missing secret cannot corrupt a draft.
	"""
	body = str(article.get("body_markdown", ""))
	if not body.strip():
		return article
	if has_footer(body, cfg):
		return article
	article["body_markdown"] = body.rstrip() + footer(cfg)
	return article