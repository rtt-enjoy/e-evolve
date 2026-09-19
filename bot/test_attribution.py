from unittest.mock import patch
import unittest

from bot.earning import attribution


class AttributionReceiptTest(unittest.TestCase):
    def _status(self, wallet):
        return {
            'wallet': wallet,
            'article_stats': {
                'count': 3,
                'total_views': 300,
                'best_title': 'A working workaround',
                'best_url': 'https://example.test/article',
                'best_views': 200,
                'winning_tags': ['python', 'automation'],
            },
            'article_interest': {
                'best_archetype': 'problem-workaround',
            },
            'payout': {
                'network': 'TRC-20 (Tron)',
                'asset': 'USDT',
            },
        }

    def _record(self, status, wallet):
        status['wallet'] = wallet
        with patch.object(
            attribution,
            'config',
            return_value={'enabled': True, 'history_limit': 10},
        ):
            return attribution.record_receipt(status)

    def test_repeated_poll_does_not_double_count(self):
        wallet = {
            'last_received_usd': '12.50',
            'last_received_at': '2026-09-19T01:00:00+00:00',
            'network': 'TRC-20',
        }
        status = self._status(wallet)

        first = self._record(status, wallet)
        duplicate = self._record(status, wallet)

        self.assertIsNotNone(first)
        self.assertIsNone(duplicate)
        self.assertEqual(status['attribution']['receipt_count'], 1)
        self.assertEqual(status['attribution']['total_attributed_usd'], 12.5)
        self.assertEqual(attribution.summary(status)['receipt_count'], 1)

    def test_same_tx_is_deduplicated_when_poll_timestamp_changes(self):
        first_wallet = {
            'last_received_usd': '12.50',
            'last_received_at': '2026-09-19T01:00:00+00:00',
            'last_received_tx': 'tx-example-1',
            'network': 'TRC-20',
        }
        repeated_wallet = {
            'last_received_usd': '12.50',
            'last_received_at': '2026-09-19T01:05:00+00:00',
            'last_received_tx': 'tx-example-1',
            'network': 'TRC-20',
        }
        status = self._status(first_wallet)

        self._record(status, first_wallet)
        duplicate = self._record(status, repeated_wallet)

        self.assertIsNone(duplicate)
        self.assertEqual(status['attribution']['receipt_count'], 1)
        self.assertEqual(status['attribution']['total_attributed_usd'], 12.5)

    def test_invalid_amount_is_ignored(self):
        wallet = {
            'last_received_usd': 'not-a-number',
            'last_received_at': '2026-09-19T01:00:00+00:00',
            'network': 'TRC-20',
        }
        status = self._status(wallet)

        self.assertIsNone(self._record(status, wallet))
        self.assertNotIn('attribution', status)


if __name__ == '__main__':
    unittest.main()