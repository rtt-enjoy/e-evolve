from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from . import _shared

log = logging.getLogger(__name__)

DEFAULTS: dict[str, Any] = {
	"enabled": True,
	"history_limit": 200,
}


def config() -> dict[str, Any]:
	"""This module's slice of config/strategy.json, read at call time."""
	return _shared.load_config("attribution", DEFAULTS)


def _live_context(status: dict[str, Any]) -> dict[str, Any]:
	"""What was published and performing when money arrived.

    Read from the snapshots the reach loop already wrote this cycle, so this
    costs no extra dev.to request. Every field is optional: a receipt during a
    dev.to outage still gets recorded, just with less around it.
    """
	stats = status.get("article_stats") or {}
	interest = status.get("article_interest") or {}
	payout = status.get("payout") or {}
	return {
		"posts_live":     int(stats.get("count") or 0),
		"total_views":    int(stats.get("total_views") or 0),
		"best_title":     str(stats.get("best_title") or "") or None,
		"best_url":       str(stats.get("best_url") or "") or None,
		"best_views":     int(stats.get("best_views") or 0),
		"winning_tags":   [str(t) for t in (stats.get("winning_tags") or [])][:6],
		"best_archetype": interest.get("best_archetype") or None,
		"footer_network": payout.get("network") or None,
		"top_post_engagement": int(stats.get("best_views") or 0),
		"top_post_url":   str(stats.get("best_url") or ""),
	}


def _defaults() -> dict[str, Any]:
	return {
		"receipts":             [],
		"receipt_count":        0,
		"total_attributed_usd": 0.0,
		"last_receipt_at":      None,
		"by_archetype":         [],
		"by_tag":               [],
		"note": (
			"Correlated context at receipt time. A TRC-20 transfer carries no "
			"memo, so this records which posts were live when money landed, "
			"not proof of which one earned it."
		),
	}


def record_receipt(status: dict[str, Any]) -> dict[str, Any] | None:
	"""Log the publishing context for a real on-chain receipt.

    Returns the new record, or None when no money arrived this cycle (the
    normal case). Called from the status phase after the wallet is polled, so
    the amount it reports is the one the chain confirmed -- this function never
    computes a dollar figure of its own.
    """
	try:
		cfg = config()
		if not cfg.get("enabled"):
			return None

		wallet = status.get("wallet") or {}
		amount = float(wallet.get("last_received_usd") or 0.0)
		if amount <= 0:
			return None

		record = {
			"at":         wallet.get("last_received_at")
				or datetime.now(timezone.utc).isoformat(),
			"amount_usd": round(amount, 6),
			"network":    wallet.get("network") or None,
			"confidence": "correlated",
			"context":    _live_context(status),
		}

		book = status.setdefault("attribution", _defaults())
		receipts: list = book.setdefault("receipts", [])
		receipts.append(record)
		limit = int(cfg.get("history_limit") or DEFAULTS["history_limit"])
		if len(receipts) > limit:
			receipts[:] = receipts[-limit:]

		book["receipt_count"] = len(receipts)
		book["total_attributed_usd"] = round(
			sum(float(r.get("amount_usd") or 0.0) for r in receipts), 6)
		book["last_receipt_at"] = record["at"]
		book["by_archetype"] = _by_archetype(receipts)
		book["by_tag"] = _by_tag(receipts)
		book.setdefault("note", _defaults()["note"])

		log.info(
			"[attribution] recorded +$%.6f against %d live posts (best: %s)",
			amount, record["context"]["posts_live"],
			record["context"]["best_title"] or "unknown",
		)
		return record
	except Exception as exc:
		log.warning("[attribution] receipt not recorded: %s", exc)
		return None


def _by_archetype(receipts: list) -> list[dict[str, Any]]:
	"""Total received while each archetype was the account's top performer."""
	buckets: dict[str, dict[str, Any]] = {}
	for rec in receipts:
		key = ((rec.get("context") or {}).get("best_archetype")) or "unknown"
		slot = buckets.setdefault(key, {"archetype": key, "count": 0, "usd": 0.0})
		slot["count"] += 1
		slot["usd"] = round(slot["usd"] + float(rec.get("amount_usd") or 0.0), 6)
	return sorted(buckets.values(), key=lambda b: b["usd"], reverse=True)


def _by_tag(receipts: list) -> list[dict[str, Any]]:
	"""Same, per winning tag. A tag counts once per receipt it was live for."""
	buckets: dict[str, dict[str, Any]] = {}
	for rec in receipts:
		amount = float(rec.get("amount_usd") or 0.0)
		for tag in ((rec.get("context") or {}).get("winning_tags") or []):
			slot = buckets.setdefault(str(tag), {"tag": str(tag), "count": 0, "usd": 0.0})
			slot["count"] += 1
			slot["usd"] = round(slot["usd"] + amount, 6)
	return sorted(buckets.values(), key=lambda b: b["usd"], reverse=True)[:12]


def summary(status: dict[str, Any]) -> dict[str, Any]:
	"""Attribution state, with the empty case spelled out rather than implied."""
	book = status.get("attribution") or _defaults()
	by_arch = book.get("by_archetype") or []
	return {
		"receipt_count":        int(book.get("receipt_count") or 0),
		"total_attributed_usd": float(book.get("total_attributed_usd") or 0.0),
		"last_receipt_at":      book.get("last_receipt_at"),
		"top_archetype":        (by_arch[0].get("archetype") if by_arch else None),
	}