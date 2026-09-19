from __future__ import annotations

import unittest
from datetime import datetime, timezone

from bot.earning import attribution


class AttributionIdempotencyTests(unittest.TestCase):
    """Regression coverage for receipt deduplication.

    A wallet poll can surface the same last receipt more than once. The
    attribution module must record it exactly once, so receipt_count and
    total_attributed_usd stay honest across repeated polls.
    """

    def _status_with_receipt(self, amount: float, at: str) -> dict:
        return {
            "wallet": {
                "last_received_usd": amount,
                "last_received_at": at,
                "network": "TRC-20",
            },
            "article_stats": {
                "count": 1,
                "total_views": 10,
                "best_title": "Sample Post",
                "best_url": "https://dev.to/example/sample-post",
                "best_views": 10,
                "winning_tags": ["python"],
            },
            "article_interest": {"best_archetype": "problem-workaround"},
            "payout": {"network": "TRC-20 (Tron)"},
        }

    def test_same_receipt_recorded_once(self) -> None:
        """Two polls reporting the same receipt must yield one record."""
        at = datetime.now(timezone.utc).isoformat()
        status = self._status_with_receipt(5.0, at)

        first = attribution.record_receipt(status)
        second = attribution.record_receipt(status)

        self.assertIsNotNone(first)
        self.assertIsNone(second, "duplicate receipt should not be recorded")
        book = status["attribution"]
        self.assertEqual(book["receipt_count"], 1)
        self.assertEqual(book["total_attributed_usd"], 5.0)
        self.assertEqual(len(book["receipts"]), 1)

    def test_different_receipts_both_recorded(self) -> None:
        """Distinct receipts must both be kept."""
        t0 = datetime(2026, 9, 18, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        t1 = datetime(2026, 9, 19, 10, 0, 0, tzinfo=timezone.utc).isoformat()
        status = self._status_with_receipt(3.0, t0)

        attribution.record_receipt(status)
        status["wallet"]["last_received_usd"] = 7.0
        status["wallet"]["last_received_at"] = t1
        attribution.record_receipt(status)

        book = status["attribution"]
        self.assertEqual(book["receipt_count"], 2)
        self.assertEqual(book["total_attributed_usd"], 10.0)
        self.assertEqual(len(book["receipts"]), 2)

    def test_zero_amount_is_not_a_receipt(self) -> None:
        """A zero-dollar poll must not create a record."""
        status = self._status_with_receipt(0.0, datetime.now(timezone.utc).isoformat())
        self.assertIsNone(attribution.record_receipt(status))
        self.assertNotIn("attribution", status)

    def test_summary_reflects_records(self) -> None:
        """summary() must agree with the recorded receipts."""
        at = datetime.now(timezone.utc).isoformat()
        status = self._status_with_receipt(5.0, at)
        attribution.record_receipt(status)
        summary = attribution.summary(status)
        self.assertEqual(summary["receipt_count"], 1)
        self.assertEqual(summary["total_attributed_usd"], 5.0)
        self.assertEqual(summary["top_archetype"], "problem-workaround")


if __name__ == "__main__":
    unittest.main()